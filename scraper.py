import requests
from bs4 import BeautifulSoup
import json
import logging
import time
import boto3

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("scraper.log", encoding="utf-8"), 
        logging.StreamHandler()                              
    ]
)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

filters = {}
filters['priceMax'] = 600000
filters['roomNumbers'] = 2
filters['roomForm'] = "pokoje" if filters['roomNumbers'] > 1 else "pokojowe"
filters['city'] = "warszawa"
filters['province'] = "mazowieckie"

URL_w_filters = f"https://www.otodom.pl/pl/wyniki/sprzedaz/mieszkanie%2C{filters.get('roomNumbers')}-{filters.get('roomForm')}/{filters.get('province')}/{filters.get('city')}/{filters.get('city')}/{filters.get('city')}?limit=36&ownerTypeSingleSelect=ALL&priceMax={filters.get('priceMax')}&by=DEFAULT&direction=DESC"

response_default = requests.get(URL_w_filters,headers=HEADERS)
soup_default = BeautifulSoup(response_default.text,'html.parser')
script_tag_default = soup_default.find('script', id='__NEXT_DATA__')
data_json_default = json.loads(script_tag_default.string)

if(data_json_default['props']['pageProps']['data']['searchAds']['pagination']['totalPages']):
    total_pages = data_json_default['props']['pageProps']['data']['searchAds']['pagination']['totalPages']
else:
    total_pages = 0

s3_client = boto3.client('s3')
BUCKET_NAME = "jucygan-otodom-raw-data-bronze"

for page_number in range(1,total_pages + 1):
    OBJECT_NAME = f"otodom_raw_data_page_{page_number}.json"
    current_url = f"{URL_w_filters}&page={page_number}"
    response = requests.get(current_url,headers=HEADERS)

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
                logging.info(f"Advertisements found: {len(ads)}. Uploading to S3...")

                s3_client.put_object(
                    Bucket=BUCKET_NAME,
                    Key=OBJECT_NAME,
                    Body=json.dumps(ads, ensure_ascii=False, indent=4),
                    ContentType="application/json"
                )

                logging.info(f"Successfully uploaded {OBJECT_NAME} to S3")
            else:
                logging.error(f"List of advertisements not found")
        else:
            logging.error(f"Json not found")
    logging.info("Waiting for 2 second before scraping next page...")
    time.sleep(2)
