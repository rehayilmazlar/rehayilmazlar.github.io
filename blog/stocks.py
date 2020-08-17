import  requests
from bs4 import BeautifulSoup

r = requests.get("https://uzmanpara.milliyet.com.tr/canli-borsa/")

source = BeautifulSoup(r.content,"lxml")

usd = source.find(id='usd_header_son_data').get_text()
eur = source.find(id='eur_header_son_data').get_text()
gold =source.find(id='gld_header_son_data').get_text()


def usdTotry():
    return usd
def eurTotry():
    return eur
def goldTotry():
    return gold