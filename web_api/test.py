import requests


r = requests.get("http://127.0.0.1:8000/search", {"search": "five nights at freddys"})
#r = requests.get("https://is-it-cracked-web.vercel.app/game-status", {"url": "https://omycrack.com/g/557970"})
print(r.json())



