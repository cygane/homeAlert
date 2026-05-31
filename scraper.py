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
        data_json = json.loads(script_tag.string)
        ads = data_json['props']['pageProps']['data']['searchAds']['items']

        if(ads):
            logging.info(f"Advertisements scraped")
            cleaned_data = []
            for ad in ads:
                data = {}
                data['id'] = ad.get('id')
                data['slug'] = ad.get('slug')

                location = ad.get('location')
                if(location and location.get('reverseGeocoding') and len(location.get('reverseGeocoding').get('locations', [])) > 2):
                    data['district'] = location['reverseGeocoding']['locations'][2].get('name')
                else:
                    data['district'] = None

                data['roomsNumber'] = ad.get('roomsNumber')
                data['floorNumber'] = ad.get('floorNumber')
                data['pricePerSquareMeter'] = ad.get('pricePerSquareMeter').get('value') if ad.get('pricePerSquareMeter') else None
                data['totalPrice'] = ad.get('totalPrice').get('value') if ad.get('totalPrice') else None
                data['areaInSquareMeters'] = ad.get('areaInSquareMeters')
                data['rentPrice'] = ad.get('rentPrice').get('value') if ad.get('rentPrice') else None
                cleaned_data.append(data)

            with open("results.json", "w", encoding="utf-8") as f:
                json.dump(cleaned_data, f, indent=4, ensure_ascii=False)
            
            logging.info(f"Saved {len(cleaned_data)} advertisements in file results.json")
        else:
            logging.error(f"List of advertisements not found")
    else:
        logging.error(f"Json not found")