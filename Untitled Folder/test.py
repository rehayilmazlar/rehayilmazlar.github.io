import requests
from bs4 import BeautifulSoup
import re
response = requests.get("https://www.imdb.com/chart/top/")

html_content = response.content
soup = BeautifulSoup(html_content, "html.parser")

dolar = soup.find_all("td", {"class":"titleColumn"})

for i in dolar:
    i = i.text
    i = i.strip().replace("\n","").replace("      ","")
    print(i)
    print("***********************")