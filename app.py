import logging
import socket
from flask import Flask, request, jsonify
from routes import app
import heapq

logger = logging.getLogger(__name__)


@app.route('/', methods=['GET'])
def default_route():
    return 'Python Template'

def dijkstra(graph, start, V):
    dist = [float('inf')] * V
    dist[start] = 0
    heap = [(0, start)]
    while heap:
        curr_dist, node = heapq.heappop(heap)
        if curr_dist > dist[node]:
            continue
        for neighbor, cost in graph[node]:
            nd = curr_dist + cost
            if nd < dist[neighbor]:
                dist[neighbor] = nd
                heapq.heappush(heap, (nd, neighbor))
    return dist

@app.route('/princess-diaries', methods=['POST'])
def princess_diaries():
    data = request.get_json()
    tasks = data['tasks']
    subway = data['subway']
    s0 = data['starting_station']

    stations = set()
    for t in tasks:
        stations.add(t['station'])
    for route in subway:
        stations.update(route['connection'])
    V = max(stations) + 1

    graph = [[] for _ in range(V)]
    for route in subway:
        u, v = route['connection']
        fee = route['fee']
        graph[u].append((v, fee))
        graph[v].append((u, fee))

    stations_to_run = set(t['station'] for t in tasks)
    stations_to_run.add(s0)

    shortest_paths = {}
    for station in stations_to_run:
        shortest_paths[station] = dijkstra(graph, station, V)

    tasks.sort(key=lambda x: x['start'])
    n = len(tasks)

    dp = [(0, float('inf'), -1) for _ in range(n)]

    for i in range(n):
        dp[i] = (tasks[i]['score'], shortest_paths[s0][tasks[i]['station']], -1)

    for i in range(n):
        for j in range(i):
            if tasks[j]['end'] <= tasks[i]['start']:
                score_j, fee_j, _ = dp[j]
                travel_cost = shortest_paths[tasks[j]['station']][tasks[i]['station']]
                candidate_score = score_j + tasks[i]['score']
                candidate_fee = fee_j + travel_cost
                cur_score, cur_fee, _ = dp[i]
                if (candidate_score > cur_score) or (candidate_score == cur_score and candidate_fee < cur_fee):
                    dp[i] = (candidate_score, candidate_fee, j)

    max_score = 0
    min_fee = float('inf')
    last_idx = -1
    for i in range(n):
        score, fee, _ = dp[i]
        total_fee = fee + shortest_paths[tasks[i]['station']][s0]
        if (score > max_score) or (score == max_score and total_fee < min_fee):
            max_score = score
            min_fee = total_fee
            last_idx = i

    schedule = []
    while last_idx != -1:
        schedule.append(tasks[last_idx]['name'])
        last_idx = dp[last_idx][2]
    schedule.reverse()

    return jsonify({
        "max_score": max_score,
        "min_fee": min_fee,
        "schedule": schedule
    })

logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

if __name__ == "__main__":
    app.run(host = '0.0.0.0', port= 8000, debug=True)

