from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/', methods=['GET'])
def default_route():
    return 'Python Template'

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

    dist = [[float('inf')] * V for _ in range(V)]
    for i in range(V):
        dist[i][i] = 0

    for route in subway:
        u, v = route['connection']
        fee = route['fee']
        dist[u][v] = fee
        dist[v][u] = fee

    for k in range(V):
        for i in range(V):
            for j in range(V):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]

    tasks.sort(key=lambda x: x['start'])
    n = len(tasks)

    dp = [(0, float('inf'), -1) for _ in range(n)]

    for i in range(n):
        dp[i] = (tasks[i]['score'], dist[s0][tasks[i]['station']], -1)

    for i in range(n):
        for j in range(i):
            if tasks[j]['end'] <= tasks[i]['start']:
                score_j, fee_j, _ = dp[j]
                travel_cost = dist[tasks[j]['station']][tasks[i]['station']]
                candidate_score = score_j + tasks[i]['score']
                candidate_fee = fee_j + travel_cost
                cur_score, cur_fee, _ = dp[i]
                if candidate_score > cur_score or (candidate_score == cur_score and candidate_fee < cur_fee):
                    dp[i] = (candidate_score, candidate_fee, j)

    max_score = 0
    min_fee = float('inf')
    last_idx = -1
    for i in range(n):
        score, fee, _ = dp[i]
        total_fee = fee + dist[tasks[i]['station']][s0]
        if score > max_score or (score == max_score and total_fee < min_fee):
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