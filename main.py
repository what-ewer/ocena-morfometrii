import re, os
from src.graph_parameters import GraphParameters
from src.graph_stats import GraphStats
from src.dag_generational_comparison import DAG_GenerationalComparison
from src.dag import DAG
from src.node import Node
from src.edge import Edge
from src.utils import load_dag

if __name__ == "__main__":
    pkl_stats_re = re.compile('.*P[0-9]*\\\\dag_with_stats.pkl')
    data_files = [os.path.join(path, name) for path, _, files in os.walk('.\\data') for name in files]
    graph_files = list(filter(pkl_stats_re.match, data_files)) 
    print(f"Currently avalible graph with stats files: {graph_files}")

    dag_names = []
    dags = []
    for g in graph_files:
        dag_id = g.split('data\\')[1].split('\\')[0]
        dag = load_dag(g)

        dags.append(dag)
        dag_names.append(dag_id)

    dag_gen_comparison = DAG_GenerationalComparison(dags, dag_names, 8)
    dag_gen_comparison.compare_all()