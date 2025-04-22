from typing import Dict, List, Tuple
import csv
import heapq
import math
import folium
import webbrowser
import os

# Build a list of edges as tuples by backtracking using previousNode dictionary
def buildPathEdges(node, prev):
    pathEdges = []
    while node != -1 and prev.get(node, -1) != -1:
        pathEdges.append((prev[node], node))
        node = prev[node]
    #return pathEdges changd by trinity
    return list(reversed(pathEdges))

# Build a path as a list of nodes from start to the nodeID
def buildPath(nodeID, previous):
    path = []
    while nodeID != -1:
        path.append(nodeID)
        nodeID = previous.get(nodeID, -1)
    path.reverse()
    return path

# Path to overlay on the map
def pathOnMap(nodes_file, path, output_file='webPathMap.html'):
    nodes = {}
    with open(nodes_file, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            node_id = int(row['id'])
            lat = float(row['latitude'])
            lon = float(row['longitude'])
            nodes[node_id] = (lat, lon)

    if len(path) == 0:
        print("No path.")
        return

    coords = [nodes[node] for node in path if node in nodes]
    m = folium.Map(tiles='OpenStreetMap')
    m.fit_bounds(coords)

    folium.PolyLine(coords, color='blue', weight=5, opacity=0.8).add_to(m)
    folium.Marker(location=nodes[path[0]], icon=folium.Icon(color='green')).add_to(m)
    folium.Marker(location=nodes[path[-1]], icon=folium.Icon(color='red')).add_to(m)

    m.save(output_file)
    webbrowser.open('file://' + os.path.realpath(output_file))

### Put both paths on the map, taken from RealPython
def comparePathsOnMap(nodes_file, path1, path2, output_file='comparisonMap.html'):
    nodes = {}
    with open(nodes_file, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            node_id = int(row['id'])
            lat = float(row['latitude'])
            lon = float(row['longitude'])
            nodes[node_id] = (lat, lon)

    if not path1 and not path2:
        print("No paths to visualize.")
        return

    coords_all = []
    if path1:
        coords_all.extend([nodes[n] for n in path1 if n in nodes])
    if path2:
        coords_all.extend([nodes[n] for n in path2 if n in nodes])

    m = folium.Map()
    m.fit_bounds(coords_all)

    if path1:
        coords1 = [nodes[n] for n in path1 if n in nodes]
        folium.PolyLine(coords1, color='blue', weight=6, opacity=0.9, tooltip="Dijkstra").add_to(m)

    if path2:
        coords2 = [nodes[n] for n in path2 if n in nodes]
        folium.PolyLine(coords2, color='red', weight=4, opacity=0.8, dash_array='10', tooltip="Bellman-Ford").add_to(m)

    if path1:
        folium.Marker(location=nodes[path1[0]], icon=folium.Icon(color='green'), tooltip="Start").add_to(m)
        folium.Marker(location=nodes[path1[-1]], icon=folium.Icon(color='black'), tooltip="End").add_to(m)

    m.save(output_file)
    webbrowser.open('file://' + os.path.realpath(output_file))

## Started with Algorithms in C:  Part 5: Graphs by Robert Sedgewick
## and Data Structures and Algorithms with C++ by Yasin H. Cakal
def dijkstra(graph, start, end=-1):
    dist = {node: math.inf for node in graph}
    prev = {node: -1 for node in graph}
    dist[start] = 0
    visited = set()
    queue = [(0, start)]

    while queue:
        d_u, u = heapq.heappop(queue)
        if u not in visited:
            visited.add(u)

            for v, w in graph.get(u, []):
                if dist[u] + w < dist[v]:
                    dist[v] = dist[u] + w
                    prev[v] = u
                    heapq.heappush(queue, (dist[v], v))

    if end != -1:
        if dist.get(end, math.inf) == math.inf:
            print("No path.")
            return []
        path = buildPath(end, prev)
        # Above left in for print statements and possible debugging
        return buildPathEdges(end, prev)

    for u in graph:
        if dist[u] < math.inf:
            path = buildPath(u, prev)
            # Above left in for print statements and possible debugging

    return []

# Based on pseudocode featured in slide 46 of Professor Kapoor's Discussion slides for Module 11
# and Edugator problem 13.6 - "Bellmanfored"
def bellman_ford(graph: Dict[int, List[Tuple[int, float]]], start: int, end: int = -1) -> Tuple[List[Tuple[int, int]], Dict[int, int]]:
    edge_list = []
    for source in graph:
        for destination, weight in graph[source]:
            edge_list.append((source, destination, weight))

    # Initialize distances and paths
    distance = {}
    previous = {}
    for node in graph:
        distance[node] = math.inf
        previous[node] = -1
    distance[start] = 0

    # Relax edges repeatedly
    for i in range(len(graph) - 1):
        updated = False
        for source, destination, weight in edge_list:
            if distance[source] != math.inf and distance[source] + weight < distance[destination]:
                distance[destination] = distance[source] + weight
                previous[destination] = source
                updated = True
        if not updated:
            print(f"Had to stop early.  i = {i + 1}")
            break

    # Check for negative cycles
    for source, destination, weight in edge_list:
        if distance[source] != math.inf and distance[source] + weight < distance[destination]:
            raise ValueError("Negative weight cycle detected.")

    # If yes to specific node path, find path and build path edges
    if end != -1:
        if distance.get(end, math.inf) == math.inf:
            print("No path found")
            return []
        path = buildPath(end, previous)
        print("Bellman-Ford: Distance =", distance[end], "Path:", "->".join(map(str, path)))
        return buildPathEdges(end, previous)

    # If no to specific node path, print shortest distance to all reachable nodes from start node
    for node in graph:
        if distance[node] < math.inf:
            path = buildPath(node, previous)
            print(f"Bellman-Ford: Distance from {start} to {node} = {distance[node]} Path:", "->".join(map(str, path)))

    return []

# Creates a graph while reading in CSV file
def loadEdgesCSV(file_name):
    graph = {}
    with open(file_name, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            u = int(row['u'])
            v = int(row['v'])
            w = float(row['length'])
            if u not in graph:
                graph[u] = []
            graph[u].append((v, w))
            if v not in graph:
                graph[v] = []
    return graph

def main():
    edgeFile = "edges.csv"
    nodeFile = "nodes.csv"
    graph = loadEdgesCSV(edgeFile)
    if not graph:
        print("The graph is empty.")
        return

    algorithm = input("Dijkstra, Bellman-Ford, or Compare? (D/B/C): ").upper()
    if algorithm not in ['D', 'B', 'C']:
        print("Those are not one of the options.")
        return

    start = int(input("Start node: "))
    choice = input("Full or end node? (F/E): ").upper()

    if choice == 'E':
        end = int(input("End node: "))
        if algorithm == 'D':
            dijkstra_edges, dijkstra_prev = dijkstra(graph, start, end)
            dijkstra_path = buildPath(end, dijkstra_prev)
            pathOnMap(nodeFile, dijkstra_path)
        elif algorithm == 'B':
            bellman_edges, bellman_prev = bellman_ford(graph, start, end)
            bellman_path = buildPath(end, bellman_prev)
            pathOnMap(nodeFile, bellman_path)
        elif algorithm == 'C':
            dijkstra_edges, dijkstra_prev = dijkstra(graph, start, end)
            dijkstra_path = buildPath(end, dijkstra_prev)

            bellman_edges, bellman_prev = bellman_ford(graph, start, end)
            bellman_path = buildPath(end, bellman_prev)

            comparePathsOnMap(nodeFile, dijkstra_path, bellman_path)
    elif choice == 'F':
        if algorithm == 'D':
            dijkstra(graph, start)
        elif algorithm == 'B':
            bellman_ford(graph, start)
        else:
            print("Compare only works with specific start and end nodes.")
    else:
        print("That's not valid input.")

if __name__ == "__main__":
    main()