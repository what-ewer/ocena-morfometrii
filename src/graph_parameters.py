from src.dag import DAG
from src.node import Node
from src.edge import Edge
from src.utils import load_dag, calculate_vectors_relative_angle, calculate_direction, generational_diff
import numpy as np

class GraphParameters:
    def __init__(self, graph_path, weights=[1, 1, 1, 1, 1, 0.8, 0.8, 0.6, 0.2]):
        print(f"Loading graph file {graph_path}...")
        self.load_graph(graph_path)

        print(f"Calculating centroid of edges...")
        self.set_centroid_to_edges()
        self.add_parent_to_nodes()

        print("Calculating edge directions...")
        self.set_edges_directions(weights)

        print("Calculating edges relative angles(bifurcation angles)...")
        self.set_edges_relative_angles(self.dag.root)

        print("Calculating tortuosity...")
        self.set_edges_tortuosities()

        print("Getting information about generations of edges...")
        self.find_edges_generation(max_gen=8)

        print("Getting information about volume filled with vascular structure")
        self.get_volume_filled_with_vascular_structure()

        print("Getting information about interstitial distances to nearest vessels...")
        self.set_interstitial_distances()

        # X fractal capacity

        # X area covered by vascular network

        # nbr of vessels

        # vessel length - total and avg

        # X vascular density

        # X lacunarity

        # correletion with stages of tumor aggressiveness

        # X branching index


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
        # print(self.dag['vascular_structure_volume'])
        # reconstruction = np.load('data/P07/reconstruction.npy')
        # print(np.sum(reconstruction > 0))