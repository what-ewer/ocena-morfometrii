from this import d
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import csv
import seaborn as sns

class DAG_GenerationalComparison:
    def __init__(self, dags, dag_names, max_gen=10):
        self.dags = dags
        self.dag_names = dag_names
        assert len(dags) == len(dag_names)
        self.max_gen = max_gen

    def __get_plot_comparison(self, data, title, save=True):
        figure, axis = plt.subplots(self.max_gen, 1)
        figure.set_size_inches(8, self.max_gen * 4)
        for gen in range(1, self.max_gen+1):
            axis[gen-1].set_title(f'Generation {gen}')
            axis[gen-1].plot(self.dag_names, [data[gen-1][graph] for graph in range(len(self.dags))], 'd')
            
        plt.xlabel('Liver Graph')
        plt.ylabel('Generation')
        if save:
            plt.savefig(f"results/graph_comparison_{title}")
            plt.clf()
        else:
            plt.show()

    def __get_boxplot_comparison(self, data, title, save=True):
        figure, axis = plt.subplots(self.max_gen, 1)
        figure.set_size_inches(8, self.max_gen * 4)
        plt.setp(axis, xticklabels=self.dag_names)
        for gen in range(1, self.max_gen+1):
            axis[gen-1].set_title(f'Generation {gen}')
            axis[gen-1].boxplot([data[gen-1][graph] for graph in range(len(self.dags))], showfliers=False)
            
        plt.xlabel('Liver Graph')
        plt.ylabel('Generation')
        if save:
            plt.savefig(f"results/graph_comparison_{title}")
            plt.clf()
        else:
            plt.show()

    def __generational_comparison(self, data, title, y_label, save=True):
        gens = [i+1 for i in range(self.max_gen)]
        plot_data = []
        
        for i,d in enumerate(data):
            plot_data.append(gens)
            plot_data.append(d)
            plot_data.append(".")

        plt.figure(figsize=(8,8))
        plt.plot(*plot_data)
        plt.legend(self.dag_names)
        plt.ylabel(y_label)
        plt.xlabel('Generation')
        if save:
            plt.savefig(f"results/generational_comparison_{title}")
            plt.clf()
        else:
            plt.show()

    def save_to_csv(self):
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
            'lacunarity'
        ]
        data = [
            [d['number_of_vessels'],
            d['vessel_total_length'],
            d['vessel_avg_length'],
            d['vascular_structure_volume'],
            d['vascular_network_projection_area'],
            d['projection_explant_area'],
            d['vascular_density'],
            d['branching_points'],
            d['branchings_points_per_pixel'],
            d['lacunarity']] for d in self.dags
        ]

        with open(f'results/all_dags_stats.csv', 'w') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            for d in data:
                writer.writerow(d)


    def compare_lengths(self, save=True):
        lengths_per_gen_per_graph = [[[] for _ in range(len(self.dags))] for _ in range(self.max_gen)]

        for i, d in enumerate(self.dags):
            lengths_generations = [(edge['length'], edge['generation']) for edge in d.edges]
            for e in lengths_generations:
                if (e[1]-1 < self.max_gen):
                    lengths_per_gen_per_graph[e[1]-1][i].append(e[0])

        edges_per_gen_per_graph = [[len(lengths_per_gen_per_graph[g][i]) for i in range(len(self.dags))] for g in range(self.max_gen)]
        edges_avg_len_per_graph_per_gen = [[np.average(lengths_per_gen_per_graph[g][i]) for g in range(self.max_gen)] for i in range(len(self.dags))]
        edges_per_graph_per_gen = [[edges_per_gen_per_graph[g][i] for g in range(self.max_gen)] for i in range(len(self.dags))]
        for d in edges_per_graph_per_gen:
            sd = sum(d)
            for i in range(len(d)):
                d[i] /= sd

        plt.title('Correlation mean lengths per generation')
        xd = np.array(lengths_per_gen_per_graph)
        avg_lengths_per_gen = np.empty(shape=xd.shape)
        for i, item in enumerate(xd):
            for j, graph in enumerate(item):
                avg_lengths_per_gen[i, j] = np.array(graph).mean()
        df = pd.DataFrame(avg_lengths_per_gen)
        corr_matrix = df.corr()
        sns.heatmap(corr_matrix, annot=True)
        plt.savefig(f"results/Correlation_mean_length_per_gen")
        plt.clf()

        self.__get_boxplot_comparison(lengths_per_gen_per_graph, "lengths_per_generation", True)
        self.__get_plot_comparison(edges_per_gen_per_graph, "edges_per_generation", True)
        self.__generational_comparison(edges_per_graph_per_gen, "edges_per_graph_per_gen", "edges / total edges", save)
        self.__generational_comparison(edges_avg_len_per_graph_per_gen, "avg_edges_len_per_graph_per_gen", "average edge length", save)
        
    def compare_diameters(self, save=True):
        diameters_per_gen_per_graph = [[[] for _ in range(len(self.dags))] for _ in range(self.max_gen)]
        for i, d in enumerate(self.dags):
            diameters_generations = [(edge['mean_radius'], edge['generation']) for edge in d.edges]
            for e in diameters_generations:
                if (e[1]-1 < self.max_gen):
                    diameters_per_gen_per_graph[e[1]-1][i].append(e[0])

        diameters_per_graph_per_gen = [[np.average(diameters_per_gen_per_graph[g][i]) for g in range(self.max_gen)] for i in range(len(self.dags))]

        self.__get_boxplot_comparison(diameters_per_gen_per_graph, "diameters_per_generation", True)
        self.__generational_comparison(diameters_per_graph_per_gen, "avg_diameters_per_graph_per_gen", "mean diameter", save)

    def compare_bifurcation_angles(self, save=True):
        bifurcation_angles_per_gen_per_graph = [[[] for _ in range(len(self.dags))] for _ in range(self.max_gen)]
        for i, d in enumerate(self.dags):
            angles_generations = [(edge['relative_angle'] / np.pi * 180, edge['generation']) for edge in d.edges[1:]]
            for e in angles_generations:
                if (e[1]-1 < self.max_gen):
                    bifurcation_angles_per_gen_per_graph[e[1]-1][i].append(e[0])

        self.__get_boxplot_comparison(bifurcation_angles_per_gen_per_graph, "bifurcation_angles_per_generation", True)

    def compare_tortuosities(self, save=True):
        tortuosities_per_gen_per_graph = [[[] for _ in range(len(self.dags))] for _ in range(self.max_gen)]
        for i, d in enumerate(self.dags):
            tortuosities_generations = [(edge['tortuosity'], edge['generation']) for edge in d.edges]
            for e in tortuosities_generations:
                if (e[1]-1 < self.max_gen):
                    tortuosities_per_gen_per_graph[e[1]-1][i].append(e[0])

        self.__get_boxplot_comparison(tortuosities_per_gen_per_graph, "tortuosities_per_generation", True)

    def compare_interstital_distances(self, save=True):
        interstitial_distances_per_gen_per_graph = [[[] for _ in range(len(self.dags))] for _ in range(self.max_gen)]
        for i, d in enumerate(self.dags):
            interstitial_distances_generations = [(edge['interstitial_distance'], edge['generation']) for edge in d.edges]
            for e in interstitial_distances_generations:
                if (e[1]-1 < self.max_gen):
                    interstitial_distances_per_gen_per_graph[e[1]-1][i].append(e[0])

        self.__get_boxplot_comparison(interstitial_distances_per_gen_per_graph, "interstitial_distances_angles_per_generation", True)

    def compare_dag_stats_correlation(self, save=True):
        self.save_to_csv()
        df = pd.read_csv('results/all_dags_stats.csv')
        df.columns = [
            'vessels count', 
            'total vessel len', 
            'vessel avg len', 
            'vascular structure vol', 
            'vascular network proj area',
            'projection explant area',
            'vascular density',
            'branching points',
            'branching points per pixel',
            'lacunarity'
        ]
        if save:
            fig, ax = plt.subplots()
            sns.heatmap(df.corr(method='pearson'), annot=True, fmt='.3f', 
                        cmap=plt.get_cmap('coolwarm'), cbar=False, ax=ax)
            ax.set_yticklabels(ax.get_yticklabels(), rotation="horizontal")
            plt.savefig('results/graph_correlation.png')
        else:
            corr = df.dropna().corr()
            corr.style.background_gradient(cmap='coolwarm').set_precision(3)


    def compare_all(self):
        self.compare_lengths()
        self.compare_diameters()
        self.compare_bifurcation_angles()
        self.compare_tortuosities()
        self.compare_interstital_distances()