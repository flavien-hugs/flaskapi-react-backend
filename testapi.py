import json
import requests


BASE_URL = "http://127.0.0.1:5000/recipes"

response = requests.get(BASE_URL)
recipes = response.json()

with open("fixtures/recipes.json", "w") as f:
    json.dump(recipes, f, indent=2)
