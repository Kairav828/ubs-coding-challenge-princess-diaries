import requests

url = 'http://127.0.0.1:8080/princess-diaries'
data = {
  "tasks": [
    { "name": "A", "start": 480, "end": 540, "station": 1, "score": 2 },
    { "name": "B", "start": 600, "end": 660, "station": 2, "score": 1 },
    { "name": "C", "start": 720, "end": 780, "station": 3, "score": 3 }
  ],
  "subway": [
    { "connection": [0, 1], "fee": 10 },
    { "connection": [1, 2], "fee": 10 },
    { "connection": [2, 3], "fee": 20 }
  ],
  "starting_station": 0
}

response = requests.post(url, json=data)
print(response.json())