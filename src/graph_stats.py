from src.dag import DAG
import matplotlib.pyplot as plt
import numpy as np
import csv

class GraphStats:
    def __init__(self, dag: DAG, dag_id: str = ""):
        self.dag = dag
        self.dag_id = dag_id

    def generate_all_stats(self):
        print("Generating stats about edges in graph")
        self.mean_length()

        print("Generating stats about mean diameter in graph")
        self.mean_diameter()

        print("Generating stats about bifurcation angles in graph")
        self.bifurcation_angles()

        print("Generating stats about tortuosities segments in graph")
        self.tortuosities()

        print("Generating stats about interstitial distances")
        self.interstitial_distances()

        print("Saving graph stats to CSV")
        self.save_graph_stats_to_csv()

    def stats_per_gen(self, stat):
        stats = [lg[0] for lg in stat]
        gens = [lg[1] for lg in stat]
        stats_per_gen = [[] for _ in range(max(gens))]
        for lg in stat:
            stats_per_gen[lg[1]-1].append(lg[0])
        return stats, gens, stats_per_gen

    def mean_length(self):
        lengths_generations = [(edge['length'], edge['generation']) for edge in self.dag.edges]
        lengths, generations, lengths_per_gen = self.stats_per_gen(lengths_generations)
        edges_per_gen = [len(eg) for eg in lengths_per_gen]

        plt.title('lengths count')
        plt.hist(lengths, bins=5)
        plt.xlabel('length')
        plt.ylabel('count')
        plt.savefig(f"results/{self.dag_id}_lengths")
        plt.clf()

        plt.title('lengths per generation')
        plt.boxplot(lengths_per_gen[:-1])
        plt.xlabel('generation')
        plt.ylabel('lengths')
        plt.savefig(f"results/{self.dag_id}_lengths_per_generation")
        plt.clf()

        plt.title('edges per generation')
        plt.boxplot(edges_per_gen[:-1])
        plt.xlabel('generation')
        plt.ylabel('edges count')
        plt.savefig(f"results/{self.dag_id}_edges_per_generation")
        plt.clf()

    def mean_diameter(self):
        diameters_generations = [(edge['mean_radius'], edge['generation']) for edge in self.dag.edges]
        diameters, generations, diameters_per_gen = self.stats_per_gen(diameters_generations)

        plt.title('lengths count')
        plt.hist(diameters, bins=8)
        plt.xlabel('diameter')
        plt.ylabel('count')
        plt.savefig(f"results/{self.dag_id}_diameters")
        plt.clf()

        plt.title('diameters per generation')
        plt.boxplot(diameters_per_gen[:-1])
        plt.xlabel('generation')
        plt.ylabel('diameters')
        plt.savefig(f"results/{self.dag_id}_diameters_per_generation")
        plt.clf()

    def bifurcation_angles(self):
        angles_generations = [(edge['relative_angle'] / np.pi * 180, edge['generation']) for edge in self.dag.edges[1:]]
        angles, generations, angles_per_gen = self.stats_per_gen(angles_generations)

        plt.title('bifurcation angles count')
        plt.hist(angles, bins=18)
        plt.xlabel('angle')
        plt.ylabel('count')
        plt.savefig(f"results/{self.dag_id}_bifurcation_angles")
        plt.clf()

        plt.title('bifurcation angles per generation')
        plt.boxplot(angles_per_gen[:-1])
        plt.xlabel('generation')
        plt.ylabel('angles')
        plt.savefig(f"results/{self.dag_id}_bifurcation_angles_per_generation")
        plt.clf()

    def tortuosities(self):
        angles_generations = [(edge['tortuosity'], edge['generation']) for edge in self.dag.edges]
        tortuosities, generations, tortuosities_per_gen = self.stats_per_gen(angles_generations)

        plt.title('segments tortuosisities count')
        plt.hist(tortuosities, bins=8)
        plt.xlabel('tortuosities segments')
        plt.ylabel('count')
        plt.savefig(f"results/{self.dag_id}_tortuosities")
        plt.clf()

        plt.title('segments tortuosities per generation')
        plt.boxplot(tortuosities_per_gen[:-1])
        plt.xlabel('generation')
        plt.ylabel('tortuosities segments')
        plt.savefig(f"results/{self.dag_id}_tortuosities_per_generation")
        plt.clf()

    def interstitial_distances(self):
        int_dist_generations = [(edge['interstitial_distance'], edge['generation']) for edge in self.dag.edges]
        int_distances, generations, int_dist_per_gen = self.stats_per_gen(int_dist_generations)

        plt.title('interstitial distances')
        plt.hist(int_distances, bins=8)
        plt.xlabel('interstitial distance')
        plt.ylabel('count')
        plt.savefig(f"results/{self.dag_id}_interstitial_distance")
        plt.clf()

        plt.title('interstitial distances per generation')
        plt.boxplot(int_dist_per_gen[:-1])
        plt.xlabel('generation')
        plt.ylabel('interstitial distance')
        plt.savefig(f"results/{self.dag_id}_interstitial_distance_per_generation")
        plt.clf()
    
    def save_graph_stats_to_csv(self):
        header = [
            'number_of_vessels',
            'vessel_total_length',
            'vessel_avg_length',
            'vascular_structure_volume',
            'vascular_network_projection_area',
            'projection_explant_area',
            'vascular_density',
            'branching_points',
            'branchings_points_per_pixel',
            'lacunarity',
        ]
        data = [
            self.dag['number_of_vessels'],
            self.dag['vessel_total_length'],
            self.dag['vessel_avg_length'],
            self.dag['vascular_structure_volume'],
            self.dag['vascular_network_projection_area'],
            self.dag['projection_explant_area'],
            self.dag['vascular_density'],
            self.dag['branching_points'],
            self.dag['branchings_points_per_pixel'],
            self.dag['lacunarity'],
        ]

        with open(f'results/{self.dag_id}_stats.csv', 'w') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerow(data)
