import re, os
from src.graph_parameters import GraphParameters
from src.graph_stats import GraphStats
from src.dag_generational_comparison import DAG_GenerationalComparison
from src.dag import DAG
from src.node import Node
from src.edge import Edge

if __name__ == "__main__":
    pkl_re = re.compile('.*P[0-9]*\\\\dag.pkl')
    data_files = [os.path.join(path, name) for path, _, files in os.walk('.\\data') for name in files]
    graph_files = list(filter(pkl_re.match, data_files)) 
    print(f"Currently avalible graph files: {graph_files}")

    dag_names = []
    dags = []

    for g in graph_files:
        dag_id = g.split('data\\')[1].split('\\')[0]
        rec_file = g.split('dag.pkl')[0] + 'reconstruction.npy'
        gp = GraphParameters(g, rec_file, dag_id=dag_id)
        gs = GraphStats(gp.dag, dag_id)
        gs.generate_all_stats()

        dags.append(gp.dag)
        dag_names.append(dag_id)

    dag_gen_comparison = DAG_GenerationalComparison(dags, dag_names, 8)
    dag_gen_comparison.compare_all()