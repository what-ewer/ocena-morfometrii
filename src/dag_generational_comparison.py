import matplotlib.pyplot as plt
import numpy as np

class DAG_GenerationalComparison:
    def __init__(self, dags, dag_names, max_gen=8):
        self.dags = dags
        self.dag_names = dag_names
        assert len(dags) == len(dag_names)
        self.max_gen = max_gen

    def __get_plot_comparison(self, data, title):
        figure, axis = plt.subplots(self.max_gen, 1)
        figure.set_size_inches(8, self.max_gen * 4)
        for gen in range(1, self.max_gen+1):
            axis[gen-1].set_title(f'Generation {gen}')
            axis[gen-1].plot(self.dag_names, [data[gen-1][graph] for graph in range(len(self.dags))], 'd')
            
        plt.xlabel('Liver Graph')
        plt.ylabel('Generation')
        plt.show()
        plt.savefig(f"results/graph_comparison_{title}")
        plt.clf()

    def __get_boxplot_comparison(self, data, title):
        figure, axis = plt.subplots(self.max_gen, 1)
        figure.set_size_inches(8, self.max_gen * 4)
        plt.setp(axis, xticklabels=self.dag_names)
        for gen in range(1, self.max_gen+1):
            axis[gen-1].set_title(f'Generation {gen}')
            axis[gen-1].boxplot([data[gen-1][graph] for graph in range(len(self.dags))], showfliers=False)
            
        plt.xlabel('Liver Graph')
        plt.ylabel('Generation')
        plt.savefig(f"results/graph_comparison_{title}")
        plt.clf()

    def __compare_lengths(self):
        lengths_per_gen_per_graph = [[[] for _ in range(len(self.dags))] for _ in range(self.max_gen)]

        for i, d in enumerate(self.dags):
            lengths_generations = [(edge['length'], edge['generation']) for edge in d.edges]
            for e in lengths_generations:
                if (e[1]-1 < self.max_gen):
                    lengths_per_gen_per_graph[e[1]-1][i].append(e[0])

        edges_per_gen_per_graph = [[len(lengths_per_gen_per_graph[g][i]) for i in range(len(self.dags))] for g in range(self.max_gen)]

        self.__get_boxplot_comparison(lengths_per_gen_per_graph, "lengths_per_generation")
        self.__get_plot_comparison(edges_per_gen_per_graph, "edges_per_generation")
        
    def __compare_diameters(self):
        diameters_per_gen_per_graph = [[[] for _ in range(len(self.dags))] for _ in range(self.max_gen)]
        for i, d in enumerate(self.dags):
            diameters_generations = [(edge['mean_radius'], edge['generation']) for edge in d.edges]
            for e in diameters_generations:
                if (e[1]-1 < self.max_gen):
                    diameters_per_gen_per_graph[e[1]-1][i].append(e[0])

        self.__get_boxplot_comparison(diameters_per_gen_per_graph, "diameters_per_generation")

    def __compare_bifurcation_angles(self):
        bifurcation_angles_per_gen_per_graph = [[[] for _ in range(len(self.dags))] for _ in range(self.max_gen)]
        for i, d in enumerate(self.dags):
            angles_generations = [(edge['relative_angle'] / np.pi * 180, edge['generation']) for edge in d.edges[1:]]
            for e in angles_generations:
                if (e[1]-1 < self.max_gen):
                    bifurcation_angles_per_gen_per_graph[e[1]-1][i].append(e[0])

        self.__get_boxplot_comparison(bifurcation_angles_per_gen_per_graph, "bifurcation_angles_per_generation")

    def __compare_tortuosities(self):
        tortuosities_per_gen_per_graph = [[[] for _ in range(len(self.dags))] for _ in range(self.max_gen)]
        for i, d in enumerate(self.dags):
            tortuosities_generations = [(edge['tortuosity'], edge['generation']) for edge in d.edges]
            for e in tortuosities_generations:
                if (e[1]-1 < self.max_gen):
                    tortuosities_per_gen_per_graph[e[1]-1][i].append(e[0])

        self.__get_boxplot_comparison(tortuosities_per_gen_per_graph, "tortuosities_per_generation")

    def __compare_interstitial_distances(self):
        interstitial_distances_per_gen_per_graph = [[[] for _ in range(len(self.dags))] for _ in range(self.max_gen)]
        for i, d in enumerate(self.dags):
            interstitial_distances_generations = [(edge['interstitial_distance'], edge['generation']) for edge in d.edges]
            for e in interstitial_distances_generations:
                if (e[1]-1 < self.max_gen):
                    interstitial_distances_per_gen_per_graph[e[1]-1][i].append(e[0])

        self.__get_boxplot_comparison(interstitial_distances_per_gen_per_graph, "interstitial_distances_angles_per_generation")

    def compare_all(self):
        self.__compare_lengths()
        self.__compare_diameters()
        self.__compare_bifurcation_angles()
        self.__compare_tortuosities()
        self.__compare_interstitial_distances()