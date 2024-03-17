import requests


#r = requests.get("http://127.0.0.1:8000/search", {"search": "fjsdfsldjkafk"})
r = requests.get("http://127.0.0.1:8000/game-status", {"url": "https://omycrack.com/g/557970"})
print(r.json())



