from src.dag import DAG
from src.utils import get_lengths, get_diameters
import matplotlib.pyplot as plt
import numpy as np

class GraphStats:
    def __init__(self, dag: DAG):
        self.dag = dag

    def generate_all_stats(self):
        print("Generating stats about mean length in graph")
        self.mean_length()

        print("Generating stats about mean diameter in graph")
        self.mean_diameter()

        print("Generating stats about bifurcation angles in graph")
        self.bifurcation_angles()

    def mean_length(self):
        lengths_generations = get_lengths(self.dag.root)
        lengths = [lg[0] for lg in lengths_generations]
        generations = [lg[1] for lg in lengths_generations]
        lengths_per_gen = [[] for _ in range(max(generations))]
        for lg in lengths_generations:
            lengths_per_gen[lg[1]-1].append(lg[0])

        plt.title('lengths count')
        plt.hist(lengths, bins=5)
        plt.xlabel('Length')
        plt.ylabel('Count')
        plt.savefig(f"results/lengths")
        plt.clf()

        plt.title('lengths per generation')
        plt.boxplot(lengths_per_gen)
        plt.xlabel('Generation')
        plt.ylabel('Lengths')
        plt.savefig(f"results/lengths_per_generation")
        plt.clf()

    def mean_diameter(self):
        diameters_generations = get_diameters(self.dag.root)
        diameters = [lg[0] for lg in diameters_generations]
        generations = [lg[1] for lg in diameters_generations]
        diameters_per_gen = [[] for _ in range(max(generations))]
        for lg in diameters_generations:
            diameters_per_gen[lg[1]-1].append(lg[0])

        plt.title('lengths count')
        plt.hist(diameters, bins=8)
        plt.xlabel('Diameter')
        plt.ylabel('Count')
        plt.savefig(f"results/diameters")
        plt.clf()

        plt.title('diameters per generation')
        plt.boxplot(diameters_per_gen)
        plt.xlabel('Generation')
        plt.ylabel('Diameters')
        plt.savefig(f"results/diameters_per_generation")
        plt.clf()

    def bifurcation_angles(self):
        angles_generations = [(edge['relative_angle'] / np.pi * 180, edge['generation']) for edge in self.dag.edges[1:]]
        angles = [a[0] for a in angles_generations]
        generations = [a[1] for a in angles_generations]
        angles_per_gen = [[] for _ in range(max(generations))]
        for ag in angles_generations:
            angles_per_gen[ag[1]-1].append(ag[0])

        plt.title('bifurcation angles count')
        plt.hist(angles, bins=18)
        plt.xlabel('Angle')
        plt.ylabel('Count')
        plt.savefig(f"results/bifurcation_angles")
        plt.clf()

        plt.title('bifurcation angles per generation')
        plt.boxplot(angles_per_gen)
        plt.xlabel('Generation')
        plt.ylabel('Angles')
        plt.savefig(f"results/bifurcation_angles_per_generation")
        plt.clf()