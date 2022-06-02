from src.dag import DAG
from src.node import Node
from src.edge import Edge
from src.dag_visualizer import DAG_Visualizer
from src.utils import load_dag, save_dag, calculate_vectors_relative_angle, calculate_direction, generational_diff
import numpy as np
from sklearn.decomposition import PCA
from skimage.morphology import convex_hull_image
from scipy.signal import fftconvolve

class GraphParameters:
    def __init__(self, 
            graph_path, # path to graph file
            reconstruction_path = None,  # path to reconstruction (if want to get 3d parameters)
            max_gen = 8,
            edge_dir_weights = [1, 1, 1, 1, 1, 0.8, 0.8, 0.6, 0.2]):

        print(f"Loading graph file {graph_path}...")
        self.load_graph(graph_path)

        print(f"Calculating centroid of edges...")
        self.set_centroid_to_edges()
        self.add_parent_to_nodes()

        print("Calculating edge directions...")
        self.set_edges_directions(edge_dir_weights)

        print("Calculating edges relative angles(bifurcation angles)...")
        self.set_edges_relative_angles(self.dag.root)

        print("Calculating tortuosity...")
        self.set_edges_tortuosities()

        print("Getting information about generations of edges...")
        self.find_edges_generation(max_gen)

        print("Getting information about number of vessels")
        self.get_number_of_vessels()

        print("Getting information about vessel average and total length")
        self.get_vessel_length()

        print("Getting information about volume filled with vascular structure")
        self.get_volume_filled_with_vascular_structure()

        print("Getting information about interstitial distances to nearest vessels...")
        self.set_interstitial_distances()

        # parameters absed on reconstruction instead of graph
        if reconstruction_path:
            print("Loading reconstruction...")
            self.reconstruction = np.load(reconstruction_path)

            print("Getting vascular network area in 2d")
            self.get_vascular_network_area()

            print("Getting vascular density...")
            self.vascular_density()

            print("Calculating branching index...")
            self.get_branching_index()

            print("Calcularing lacunarity")
            self.get_lacunarity()

        print("Saving graph file...")
        save_dag(self.dag, "results/dag_with_stats.pkl")


    ####################################################################################
    #                                  LOADING GRAPH                                   #
    ####################################################################################

    def load_graph(self, graph_path):
        try:
            self.dag = load_dag(graph_path)
        except Exception as ex:
            raise Exception(f'Could not load graph file - {ex}')
            

    ####################################################################################
    #                                CENTROID, PARENT                                  #
    ####################################################################################

    def set_centroid_to_edges(self):
        for e in self.dag.edges:
            e['centroid'] = np.mean(e['voxels'], axis=0)

    def add_parent_to_nodes(self):
        self.dag.root['parent'] = None
        for e in self.dag.edges:
            e.node_b['parent'] = e.node_a


    ####################################################################################
    #                                 EDGE DIRECTIONS                                  #
    ####################################################################################

    def calculate_edge_directions(self, edge, weights):
        start_point = edge.node_a['centroid']
        end_point = edge.node_b['centroid']
        start_direction = calculate_direction(start_point, edge['voxels'], weights)
        end_direction = calculate_direction(end_point, np.flip(edge['voxels'], axis=0), weights) * (-1)
        return start_direction, end_direction

    def set_edges_directions(self, weights=[1, 1, 1, 1, 0.6, 0.2]): 
        for edge in self.dag.edges:
            start_direction, end_direction = self.calculate_edge_directions(edge, weights)
            edge['start_direction'] = start_direction
            edge['end_direction'] = end_direction
   

    ####################################################################################
    #                              EDGE RELATIVE ANGLES                                #
    ####################################################################################

    def set_edges_relative_angles(self, node, parent_edge=None):
        for edge in node.edges:
            if parent_edge is not None:
                edge['relative_angle'] = calculate_vectors_relative_angle(
                    parent_edge['end_direction'], edge['start_direction'])
            else:
                edge['relative_angle'] = None
                    
            self.set_edges_relative_angles(edge.node_b, edge)


    ####################################################################################
    #                                   TORTUOSITY                                     #
    ####################################################################################

    def set_edges_tortuosities(self): 
        for edge in self.dag.edges:
            chord_length = np.linalg.norm(edge.node_b['centroid'] - edge.node_a['centroid'])
            edge['tortuosity'] = edge['length'] / chord_length


    ####################################################################################
    #                                  GENERATIONS                                     #
    ####################################################################################

    def find_edges_generation(self, max_gen=np.inf, max_angle = np.pi / 6, max_thick_diff = 0.7):
        for e in self.dag.root.edges:
            self.get_edges_generation(e, None, max_gen, max_angle, max_thick_diff)

    def get_edges_generation(self, edge: Edge, parent=None, max_gen=np.inf, max_angle = np.pi / 6, max_thick_diff = 0.7):
        # basic condition for root
        if parent is None: 
            edge['generation'] = 1
        else:
            if generational_diff(parent, edge, max_angle, max_thick_diff):
                edge['generation'] = parent['generation']
            else:
                edge['generation'] = parent['generation'] + 1
        
        # if we reach max_gen every other gen is max_gen + 1
        if edge['generation'] > max_gen:
            edge['generation'] = max_gen + 1
                
        for e in edge.node_b.edges:
            self.get_edges_generation(e, edge, max_gen, max_angle, max_thick_diff)


    ####################################################################################
    #                           VESSELS COUNT + LENGTH                                 #
    ####################################################################################

    def vessels_recursive(self, node):
        if len(node.edges) == 0:
            return 1
        
        count = 0
        for e in node.edges:
            count += self.vessels_recursive(e.node_b)
        return count

    def vessel_length_recursive(self, edge):
        if len(edge.node_b.edges) == 0:
            return edge['length']
        
        count = 0
        for e in edge.node_b.edges:
            count += self.vessel_length_recursive(e)
        return count

    def get_number_of_vessels(self):
        self.dag['number_of_vessels'] = self.vessels_recursive(self.dag.root)

    def get_vessel_length(self):
        vessel_length = 0
        for e in self.dag.root.edges:
            vessel_length +=  self.vessel_length_recursive(e)

        self.dag['vessel_total_length'] = vessel_length
        self.dag['vessel_avg_length'] = vessel_length / self.dag['number_of_vessels']

    ####################################################################################
    #                              INTERSTITIAL DISTANCE                               #
    ####################################################################################
    
    def get_interstitial_distances(self, edge):
        if len(edge.node_b.edges) == 0:
            edge['interstitial_distance'] = np.linalg.norm(edge.node_b['centroid'] - edge['centroid'])
        else:
            edges = edge.node_b.edges
            min_val = np.inf
            for e in edges:
                self.get_interstitial_distances(e)
                dist =  np.linalg.norm(edge['centroid'] - e['centroid']) + e['interstitial_distance']
                if dist < min_val:
                    min_val = dist
            edge['interstitial_distance'] = min_val

    def set_interstitial_distances(self):
        for e in self.dag.root.edges:
            self.get_interstitial_distances(e)


    ####################################################################################
    #                      VOLUME FILLED WITH VASCULAR STRUCTURE                       #
    ####################################################################################

    def get_volume_filled_with_vascular_structure(self):
        sum = 0
        for e in self.dag.edges:
            sum += 2/3 * len(e['voxels']) * e['mean_radius'] * e['mean_radius'] * np.pi
        self.dag['vascular_structure_volume'] = sum


    ####################################################################################
    #                          AREA COVERED BY VASCULAR NETWORK                        #
    ####################################################################################

    def project_reconstruction(self):
        reconstruction_coords = np.argwhere(self.reconstruction > 0)
        pca = PCA(n_components=2)
        pca.fit(reconstruction_coords)
        return pca.transform(reconstruction_coords)

    def get_vascular_network_area(self):
        reconstruction_projection = self.project_reconstruction()
        rounded_reconstruction_projection = np.round(reconstruction_projection)
        mins = np.min(reconstruction_projection, axis=0)
        shifted_projection = (rounded_reconstruction_projection - mins).astype(np.int)
        self.reconstruction_projection_mask = np.zeros(np.max(shifted_projection + 1, axis=0), dtype=np.bool)
        self.reconstruction_projection_mask[shifted_projection[:, 0], shifted_projection[:, 1]] = 1
        DAG_Visualizer.vascular_network_area(self.reconstruction_projection_mask)
        self.dag['vascular_network_projection_area'] = np.sum(self.reconstruction_projection_mask)


    ####################################################################################
    #                                   VASCULAR DENSITY                               #
    ####################################################################################

    def vascular_density(self):
        self.convex_projection = convex_hull_image(self.reconstruction_projection_mask)
        DAG_Visualizer.vascular_density(self.convex_projection)
        self.dag['projection_explant_area'] = self.convex_projection.sum()
        self.dag['vascular_density'] = self.dag['vascular_network_projection_area'] / self.dag['projection_explant_area']


    ####################################################################################
    #                                   BRANCHING INDEX                                #
    ####################################################################################

    def get_number_of_branching_points(self):
        nodes_with_children = [n for n in self.dag.nodes if len(n.edges) != 0]
        branch_nodes = [n for n in nodes_with_children if n['parent'] is not None]
        return len(branch_nodes)

    def get_branching_index(self):
        self.dag['branching_points'] = self.get_number_of_branching_points()
        self.dag['branchings_points_per_pixel'] = self.dag['branching_points'] / self.dag['vascular_network_projection_area']


    ####################################################################################
    #                                     LACUNARITY                                   #
    ####################################################################################

    def calculate_one_box_lacunarity(self, box_size):
        box = np.ones((box_size, box_size))
        convolution = fftconvolve(self.reconstruction_projection_mask, box, mode='valid')
        mean_sqrd = np.mean(convolution)**2
        if mean_sqrd == 0:
            return 0.0
        return (np.var(convolution) / mean_sqrd) + 1

    def calculate_avg_lacunarity(self, box_sizes):
        lacunarities = []
        for box_size in box_sizes:
            lacunarities.append(self.calculate_one_box_lacunarity(box_size))
        return np.mean(lacunarities)

    def get_lacunarity(self):
        box_sizes = [10, 30, 50, 70, 90, 110, 130, 150]
        self.dag['lacunarity'] = self.calculate_avg_lacunarity(box_sizes)