from bs4 import BeautifulSoup
from pymongo import MongoClient
from pymongo.errors import BulkWriteError
from requests import exceptions
from conf import USER_AGENT, ROOT_URL, MAX_CARS_COUNT
from db_utilities import DbUtiltity
import requests
import re


def start_data_accquiring():
    curr_page = 1
    car_count = 0
    with DbUtiltity() as db_util:
        try:
            db_util.connect_to_db()
            db_util.drop_cars_collection()

            while car_count < MAX_CARS_COUNT:
                cars = process_one_page(curr_page)
                if len(cars) > 0:
                    db_util.save_cars_to_db(cars)

                car_count += len(cars)
                curr_page += 1

        except Exception as e:
            print(e)

    build_brand_model_relationship()

def build_brand_model_relationship():
    with DbUtiltity() as db_util:
        db_util.connect_to_db()
        db_util.drop_brand_models_collection()

        brand_model_pairs = [id['_id'] for id in db_util.find_brand_models()]
        db_util.save_brand_models(brand_model_pairs)

def process_one_page(current_page):
    cars = []

    url_str = f'{ROOT_URL}?page={current_page}'

    page = requests.get(url_str)
    page_content = BeautifulSoup(page.content, 'html.parser')

    # find list of cars
    articles = page_content.find_all('div', attrs={"class":"result-tile"})
    for article in articles:
        if article and article.a:
            # car_id
            pattern = re.compile("/vehicle/(.*)")
            result = pattern.search(article.a.get('href'))
            car_id = result.group(1).strip()

            # year and brand
            combined_str = article.find(name='div', attrs={"class":"year-make"}).get_text()
            year = int(combined_str.split()[0].strip())
            brand = combined_str.split()[1].strip()

            # model
            model = article.find(name='div', attrs={"class":"model"}).get_text()

            # mileage
            combined_str = article.find(name='div', attrs={"class":"mileage"}).get_text()
            mileage = int(combined_str.split()[0].strip().replace(",", ""))
        
            # price
            combined_str = article.find(name='div', attrs={"class":"price"}).get_text()
            price = int(combined_str.strip().replace(",", "").replace("$", ""))

            cars.append({'_id': car_id
                         , 'year': year
                         , 'brand': brand
                         , 'model': model
                         , 'mileage': mileage
                         , 'price': price})

    return cars
