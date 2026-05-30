import requests
from bs4 import BeautifulSoup
import json
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("scraper.log", encoding="utf-8"), 
        logging.StreamHandler()                              
    ]
)
URL = "https://www.otodom.pl/pl/wyniki/sprzedaz/mieszkanie%2C2-pokoje/mazowieckie/warszawa/warszawa/warszawa?limit=36&ownerTypeSingleSelect=ALL&priceMax=600000&by=DEFAULT&direction=DESC"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

response = requests.get(URL,headers=HEADERS)

if (response.status_code != 200):
    logging.error(f"Connection failed: {response.status_code}")
else:
    logging.info(f"Connection succeed")

    soup = BeautifulSoup(response.text,'html.parser')
    script_tag = soup.find('script', id='__NEXT_DATA__')
    
    if(script_tag):
        logging.info(f"Json found")
        print(script_tag.string[:500])
    else:
        logging.error(f"Json not found")