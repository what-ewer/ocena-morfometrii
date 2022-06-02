import re, os
from src.graph_parameters import GraphParameters
from src.graph_stats import GraphStats
from src.dag import DAG
from src.node import Node
from src.edge import Edge

if __name__ == "__main__":
    # pkl_re = re.compile('.*P[0-9]*\\\\dag.pkl')
    # data_files = [os.path.join(path, name) for path, _, files in os.walk('.\\data') for name in files]
    # graph_files = list(filter(pkl_re.match, data_files)) 
    # print(f"Currently avalible graph files: {graph_files}")
    graph_file = 'data/P07/dag.pkl'
    reconstruction_file = 'data/P07/reconstruction.npy'
    gp = GraphParameters(graph_file, reconstruction_file)
    gs = GraphStats(gp.dag)
    gs.generate_all_stats()
    print(gp.dag.root.data)
    print(gp.dag.root.edges[0].data)
