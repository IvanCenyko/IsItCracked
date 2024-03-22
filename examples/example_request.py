import requests

game_to_search =  "helldivers"
# request to steam-search endpoint, example helldivers
r = requests.get("http://127.0.0.1:8000/steam-search", {"search": game_to_search})

# take first of steam results
results = r.json()["results"]
print(results[0])

# request to cracked-search endpoint, returns if there's results on igg with its link
r2 = requests.get("http://127.0.0.1:8000/cracked-search-igg", {"search": results[0]})
# request to cracked-search endpoint, returns if there's results on fitgirl with its link
r3 = requests.get("http://127.0.0.1:8000/cracked-search-fitgirl", {"search": results[0]})

results_igg = r2.json()["results"]
results_fitgirl = r3.json()["results"]

print(str(results_igg) + "\n" + str(results_fitgirl))




