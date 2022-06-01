import pickle  
import numpy as np    

def get_nodes_with_dfs(root):
    nodes = [root]
    for e in root.edges:
        if e.node_a != root:
            print(e)
        nodes += get_nodes_with_dfs(e.node_b)
    return nodes

def get_edges_with_dfs(root):
    edges = []
    for e in root.edges:
        edges += [e]
        edges += get_edges_with_dfs(e.node_b)
    return edges

def save_dag(dag, filename):
    with open(filename, 'wb') as output:
        pickle.dump(dag, output)
        
def load_dag(filename):
    with open(filename, 'rb') as input_:
        dag = pickle.load(input_)
        return dag

def calculate_direction(source, points, weights):
    if len(weights) > len(points):
        weights = weights[:len(points)]
    points = points[:len(weights)]
    all_directions = points - source
    direction = np.average(all_directions, axis=0, weights=weights)
    return direction / np.linalg.norm(direction)

def calculate_vectors_relative_angle(v1, v2):
    cosine = np.dot(v1,v2)
    return np.arccos(cosine)

def generational_diff(a, b, max_angle, max_thick_diff):
    return (
        b['relative_angle'] < max_angle and 
        b['mean_radius'] > max_thick_diff * a['mean_radius']
    )

def get_lengths_recursive(edges, lengths):
    nodes = [edge.node_b for edge in edges]
    if len(nodes) == 0:
        return lengths

    new_edges = []
    for edge in edges:
        children = edge.node_b.edges
        for e in children:
            lengths.append((e['length'] / edge['length'], e['generation']))
            new_edges.append(e)
    return get_lengths_recursive(new_edges, lengths)

def get_lengths(root):
    return get_lengths_recursive(root.edges, [])

def get_diameters_recursive(edges, diameters):
    nodes = [edge.node_b for edge in edges]
    if len(nodes) == 0:
        return diameters

    new_edges = []
    for edge in edges:
        children = edge.node_b.edges
        for e in children:
            diameters.append((e['mean_radius'] / edge['mean_radius'], e['generation']))
            new_edges.append(e)
    return get_diameters_recursive(new_edges, diameters)

def get_diameters(root):
    return get_diameters_recursive(root.edges, [])