import json
import requests

url = "https://imdb8.p.rapidapi.com/title/get-awards"

querystring = {"tconst":"tt0944947"}

headers = {
    'x-rapidapi-key': "add-key-here",
    'x-rapidapi-host': "imdb8.p.rapidapi.com"
    }

response = requests.request("GET", url, headers=headers, params=querystring)

content = json.loads(response.text)

print(content["resource"]["awards"][0]["nominations"]["titles"][0]["title"])
