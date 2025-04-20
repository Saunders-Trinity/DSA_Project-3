import csv
import heapq
from typing import Dict, List, Tuple, Set

# Build a list of edges as tuples by backtracking using previousNode dictionary
def buildPathEdges(nodeID: int, previousNode: Dict[int, int]) -> List[Tuple[int, int]]:
    pathEdges = []
    while nodeID != -1 and previousNode.get(nodeID, -1) != -1:
        pathEdges.append((previousNode[nodeID], nodeID))
        nodeID = previousNode[nodeID]
    return pathEdges

# Build a path as a list of nodes from start to the nodeID
def buildPath(nodeID: int, previousNode: Dict[int, int]) -> List[int]:
    path = []
    while nodeID != -1:
        path.append(nodeID)
        nodeID = previousNode.get(nodeID, -1)
    return path

######### Citation goes here
def dijkstra(graph: Dict[int, List[Tuple[int, float]]], start: int, target: int = -1) -> List[Tuple[int, int]]:
    import math

    # Initiate paths and distances
    dist = {}
    visited = {}
    prev = {}

    for node in graph:
        dist[node] = math.inf
        visited[node] = False
        prev[node] = -1
    dist[start] = 0

    # Initiate min heap for processing the shortest distance nodes first
    pq = [(0.0, start)]

    while pq:
        # Pop and return shortest distance node in min heap
        currentDist, currentNode = heapq.heappop(pq)

        # Check if node has been visited, skip if true
        if visited[currentNode]:
            continue
        visited[currentNode] = True

        # Relax each neighbor of current node, update if shorter than previous path
        for v, w in graph.get(currentNode, []):
            newDist = currentDist + w
            if newDist < dist[v]:
                dist[v] = newDist
                prev[v] = currentNode
                heapq.heappush(pq, (newDist, v))

    # If yes to specific node path, find path and build edge
    if target != -1:
        if target not in dist or dist[target] == math.inf:
            print(f"No path from {start} to {target}")
            return []

        path = buildPath(target, prev)
        print(f"Dijkstra: The shortest path from {start} to {target} is {dist[target]}. Path: ", end="")
        print(" -> ".join(map(str, reversed(path))))
        return buildPathEdges(target, prev)

    # If no to specific node path, print shortest distance to all reachable nodes from start node
    for nodeID, distance in dist.items():
        if distance == math.inf:
            continue
        path = buildPath(nodeID, prev)
        print(f"Dijkstra: The shortest path from {start} to {nodeID} is {distance}. Path: ", end="")
        print(" -> ".join(map(str, reversed(path))))

    return []


# Based on pseudocode featured in slide 46 of Professor Kapoor's Discussion slides for Module 11
# and Edugator problem 13.6 - "Bellmanfored"
def bellman_ford(graph: Dict[int, List[Tuple[int, float]]], start: int, target: int = -1) -> List[Tuple[int, int]]:
    import math
    edge_list = []

    # from node = u, to node = v, weight = w
    for u in graph:
        for v, w in graph[u]:
            edge_list.append((u, v, w))

    # Initialize distances and paths
    distance = {}
    previous = {}

    nodes = set(graph.keys())
    for edges in graph.values():
        for v, _ in edges:
            nodes.add(v)

    for node in nodes:
        distance[node] = math.inf
        previous[node] = -1
    distance[start] = 0

    # Relax edges repeatedly with early stopping
    for i in range(len(nodes) - 1):
        updated = False
        for u, v, w in edge_list:
            if distance[u] + w < distance[v]:
                distance[v] = distance[u] + w
                previous[v] = u
                updated = True
        if not updated:
            break  # No update, optimal solution reached

    # Check for negative cycles
    for u, v, w in edge_list:
        if distance[u] + w < distance[v]:
            raise ValueError("Negative weight cycle detected.")

    # If yes to specific node path, find path and build path edges
    if target != -1:
        if distance.get(target, math.inf) == math.inf:
            print(f'No path found')
            return []
        path = buildPath(target, previous)
        print(f'Bellman-Ford: The shortest path from {start} to {target} is {distance[target]}. Path: ', end="")
        print(" -> ".join(map(str, reversed(path))))
        return buildPathEdges(target, previous)

    # Print shortest distance to all reachable nodes from start node
    for node in graph:
        if distance[node] == math.inf:
            continue
        path = buildPath(node, previous)
        print(f'Bellman-Ford: Shortest path from {start} to {node} is {distance[node]}. Path: ', end="")
        print(" -> ".join(map(str, reversed(path))))

    return []

# Creates a graph while reading in CSV file
def loadEdgesCSV(fileName: str) -> Dict[int, List[Tuple[int, float]]]:
    graph = {}
    try:
        with open(fileName, newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    fromNode = int(row['u'])
                    toNode = int(row['v'])
                    weight = float(row['length'])
                    if fromNode not in graph:
                        graph[fromNode] = []
                    graph[fromNode].append((toNode, weight))
                    if toNode not in graph:
                        graph[toNode] = []
                except:
                    continue
    except FileNotFoundError:
        print(f"Error opening file {fileName}")
        return {}
    return graph

# Export the graph in DOT format
def exportGraphToDOT(graph: Dict[int, List[Tuple[int, float]]], filename: str,
                     highlightEdges: Set[Tuple[int, int]] = set(),
                     highlightNodes: Set[int] = set()):
    with open(filename, "w") as out:
        out.write("digraph G {\n")
        out.write("    node [shape=circle, style=filled, fillcolor=white];\n")

        allNodes = set(graph.keys())
        for neighbors in graph.values():
            for to, _ in neighbors:
                allNodes.add(to)

        for node in allNodes:
            out.write(f'    "{node}"')
            if node in highlightNodes:
                out.write(" [style=filled, fillcolor=lightcoral, color=red, penwidth=2]")
            out.write(";\n")

        for fromNode, neighbors in graph.items():
            for toNode, weight in neighbors:
                out.write(f'    "{fromNode}" -> "{toNode}" [label=\"{weight}\"')
                if (fromNode, toNode) in highlightEdges:
                    out.write(", color=red, penwidth=2.5")
                out.write("];\n")

        out.write("}\n")
    print(f"DOT file with highlighted nodes and edges written to: {filename}")

# Exports a subgraph of the graph in DOT format
def exportSubgraphDOT(pathEdges: List[Tuple[int, int]],
                      graph: Dict[int, List[Tuple[int, float]]],
                      filename: str):
    pathNodes = set()
    for fromNode, toNode in pathEdges:
        pathNodes.add(fromNode)
        pathNodes.add(toNode)

    with open(filename, "w") as out:
        out.write("Directed Graph SubgraphPath {\n")
        out.write("    node [shape=circle, style=filled, fillcolor=lightcoral, color=red, penwidth=2];\n")

        for node in pathNodes:
            out.write(f'    "{node}";\n')

        for fromNode, toNode in pathEdges:
            weight = next((w for neighbor, w in graph[fromNode] if neighbor == toNode), 0.0)
            out.write(f'    "{fromNode}" -> "{toNode}" [label="{weight}", color=red, penwidth=2.5];\n')

        out.write("}\n")
    print(f"Subgraph DOT file written to: {filename}")

def main():
    edgeFile = "edges.csv"
    graph = loadEdgesCSV(edgeFile)

    if not graph:
        print("Graph loading failed or file is empty.")
        return

    algorithm = input("Which algorithm would you like, Dijkstra or Bellman-Ford? (d/b): ")
    if algorithm.lower() != 'd' and algorithm.lower() != 'b':
        print('Choice not supported.')
        return


    startNode = int(input("Enter start node ID: "))
    if startNode not in graph:
        print("Start node not found in graph.")
        return

    choice = input("Do you want to find a path to a specific node? (y/n): ")
    if choice.lower() != 'y' and choice.lower() != 'n':
        print('Choice not supported.')
        return

    try:
        if choice.lower() == 'y':
            targetNode = int(input("Enter target node ID: "))
            if algorithm.lower() == 'd':
                pathEdges = dijkstra(graph, startNode, targetNode)
            elif algorithm.lower() == 'b':
                pathEdges = bellman_ford(graph, startNode, targetNode)
            exportSubgraphDOT(pathEdges, graph, "subgraph.dot")

            highlightSet = set(pathEdges)
            pathNodes = {u for edge in pathEdges for u in edge}
            exportGraphToDOT(graph, "graph.dot", highlightSet, pathNodes)

            print("\nRendered files:")
            print("  subgraph.dot   -> contains only shortest path (fast).")
            print("  graph.dot      -> full graph with highlighted path (slow).")
        else:
            if algorithm.lower() == 'd':
                dijkstra(graph, startNode)
            elif algorithm.lower() == 'b':
                bellman_ford(graph, startNode)
            exportGraphToDOT(graph, "graph.dot")
            print("\nRendered file: graph.dot")
    except ValueError as e:
        print(f"An error has occurred: {e}")


if __name__ == "__main__":
    main()