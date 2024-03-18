import requests

r = requests.get("http://127.0.0.1:8000/search", {"search": "five nights at freddys"})
r2 = requests.get("http://127.0.0.1:8000/game-status", {"url": "https://omycrack.com/g/557970"})
print(r.json(), "\n\n", r2.json())

