import re, os
from src.graph_parameters import GraphParameters
from src.graph_stats import GraphStats
from src.dag import DAG
from src.node import Node
from src.edge import Edge

if __name__ == "__main__":
    pkl_re = re.compile('.*P[0-9]*\\\\dag.pkl')
    data_files = [os.path.join(path, name) for path, _, files in os.walk('.\\data') for name in files]
    graph_files = list(filter(pkl_re.match, data_files)) 
    print(f"Currently avalible graph files: {graph_files}")
    gp = GraphParameters(graph_files[1])
    gs = GraphStats(gp.dag)
    gs.generate_all_stats()
    print(gp.dag.root.edges[0].data)
