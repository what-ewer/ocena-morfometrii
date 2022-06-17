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

    dags = []
    for g in graph_files:
        dag_id = g.split('data\\')[1].split('\\')[0]
        dag = load_dag(g)
        dags.append((dag,dag_id))

    exclude = ["P02", "P03", "P11", "P13", "P24", "P25", "P26", "P30", "P32"]
    dags = [x for x in dags if x[1] not in exclude]

    dag_names = [d[1] for d in dags]
    dag_graphs = [d[0] for d in dags]
    dag_gen_comparison = DAG_GenerationalComparison(dag_graphs, dag_names, 8)
    dag_gen_comparison.compare_all()