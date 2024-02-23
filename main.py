import matplotlib.pyplot as plt
import networkx as nx
import random
from pathlib import Path
import math

def create_grid_graph(n):
    """Create an nxn grid graph."""
    G = nx.grid_2d_graph(n, n)
    G.graph['height'] = n
    G.graph['width'] = n
    return G

def connect_nodes_randomly(G, p=0.8, ensure_path=False, grid_size=0):
    """
    Connect nodes randomly in the graph.

    If ensure_path is True, the graph remains connected; otherwise, it may become disconnected.
    """
    # Remove non-immediate neighbor edges first
    for edge in list(G.edges()):
        if abs(edge[0][0] - edge[1][0]) + abs(edge[0][1] - edge[1][1]) > 1:
            G.remove_edge(*edge)

    # Randomly remove edges
    for edge in list(G.edges()):
        if random.random() > p:
            G.remove_edge(*edge)

    if ensure_path:
        while not nx.is_connected(G):
            components = list(nx.connected_components(G))
            u, v = random.choice(list(components[0])), random.choice(list(components[1]))
            G.add_edge(u, v)

    return G

def find_distant_connected_nodes(G, min_distance_ratio=0.5):
    """
    Find two distant nodes in the graph that are connected.
    """
    start_node = random.choice(list(G.nodes()))
    max_distance, farthest_node = 0, start_node

    for node, distance in nx.single_source_shortest_path_length(G, start_node).items():
        if distance > max_distance and distance >= min_distance_ratio * min(G.graph['height'], G.graph['width']):
            max_distance, farthest_node = distance, node

    if farthest_node == start_node:
        for neighbor in G.neighbors(start_node):
            if nx.shortest_path_length(G, start_node, neighbor) > 1:
                return start_node, neighbor
        return start_node, start_node

    return start_node, farthest_node

def draw_graph(G, selected_nodes, path, file_prefix, grid_size, has_path):
    """
    Draw the graph and save it as an image.
    """
    path_suffix = "_path" if has_path else "_no_path"
    filename = f'{file_prefix}_{grid_size}x{grid_size}{path_suffix}.png'
    
    plt.figure(figsize=(max(8, grid_size / 3), max(8, grid_size / 3)))
    pos = {node: (node[1], -node[0]) for node in G.nodes()}

    nx.draw_networkx_nodes(G, pos, node_size=40, node_color="black")
    nx.draw_networkx_edges(G, pos, edgelist=[e for e in G.edges() if abs(e[0][0] - e[1][0]) + abs(e[0][1] - e[1][1]) == 1], width=2, edge_color='black')

    if path:
        nx.draw_networkx_nodes(G, pos, nodelist=path, node_size=100, node_color='red')
        nx.draw_networkx_edges(G, pos, edgelist=list(zip(path, path[1:])), width=10, edge_color='red')

    nx.draw_networkx_nodes(G, pos, nodelist=selected_nodes, node_size=100, node_color='green')

    plt.axis('equal')
    plt.axis('off')
    plt.savefig(filename, format='png')
    plt.close()

def generate_quizzes_and_solutions(start=3, end=33, path_probability=0.5):
    """
    Generate quizzes and solutions for a range of grid sizes.
    """
    Path("quiz").mkdir(parents=True, exist_ok=True)
    Path("solution").mkdir(parents=True, exist_ok=True)

    for n in range(start, end + 1, 3):
        G = create_grid_graph(n)

        has_path = random.random() < path_probability
        if has_path:
            G = connect_nodes_randomly(G, ensure_path=True, grid_size=n)
            start_node, end_node = find_distant_connected_nodes(G)
            path = nx.shortest_path(G, start_node, end_node)
        else:
            G = connect_nodes_randomly(G, ensure_path=False, grid_size=n)
            start_node, end_node = find_distant_connected_nodes(G)
            
            while nx.has_path(G, start_node, end_node):
                path = nx.shortest_path(G, start_node, end_node)
                if len(path) > 3:
                    edges = list(zip(path, path[1:]))
                    sigma = len(edges) / 6
                    weights = [math.exp(-0.5 * ((i - len(edges) // 2) / sigma) ** 2) for i in range(len(edges))]
                    edge_to_remove = random.choices(edges, weights=weights, k=1)[0]
                    G.remove_edge(*edge_to_remove)
                else:
                    break
            path = []

        draw_graph(G, [start_node, end_node], [], 'quiz/q', n, has_path)
        draw_graph(G, [start_node, end_node], path, 'solution/s', n, has_path)

if __name__ == "__main__":
    generate_quizzes_and_solutions()