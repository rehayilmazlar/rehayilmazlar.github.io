import requests

url = "http://data.fixer.io/api/latest?access_key=fb6642b40ceb48247cf957af75f3d26a&symbols=USD,TRY"

response = requests.get(url)

json_data = response.json()

eur = json_data["rates"]["TRY"]

usd = json_data["rates"]["TRY"] / json_data["rates"]["USD"]
def usdTotry():
    return "1 USD = "+ usd + " TRY"
def eurTotry():
    return "1 EUR = "+ eur+ " TRY"