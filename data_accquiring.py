from bs4 import BeautifulSoup
from pymongo import MongoClient
from pymongo.errors import BulkWriteError
from requests import exceptions
from conf import USER_AGENT, ROOT_URL
from db_utilities import DbUtiltity
import urllib.request
import re


def start_data_accquiring():
    headers = {'User-Agent':USER_AGENT}

    # find total number of cars
    total_number_of_cars = 0
    n_tries = 0
    max_tries = 5
    while total_number_of_cars == 0 and n_tries < max_tries:
        n_tries += 1
        try:
            request = urllib.request.Request(ROOT_URL,None,headers) #The assembled request
            response = urllib.request.urlopen(request)
            content = response.read().decode()
            page_content = BeautifulSoup(content, 'html.parser')

            span_tag = page_content.find('span', attrs={"data-qa":"pagination-text"})
            pattern = re.compile("(.*)-(.*) of (.*) Results")
            result = pattern.search(span_tag.get_text())
            total_in_str = result.group(3).strip()
            total_number_of_cars = int(total_in_str)
            
        except Exception as e:
            print(e)

    #print(f'Total number of cars: {total_number_of_cars}')

    curr_page = 1
    car_count = 0
    cars_bulk = []
    with DbUtiltity() as db_util:
        try:
            if total_number_of_cars > 0:
                db_util.drop_cars_collection()

            while car_count < total_number_of_cars:
                cars = process_one_page(curr_page)
                cars_bulk.extend(cars)
                if len(cars_bulk) > 0 and (curr_page%10 == 0):
                    db_util.save_cars_to_db(cars_bulk)
                    cars_bulk = []
                    #print(f'Done processing page {curr_page}')

                car_count += len(cars)
                curr_page += 1

        except Exception as e:
            print(e)

    #print(f'Done sucessfully! Car count: {car_count}')

def process_one_page(current_page):
    cars = []

    url_str = f'{ROOT_URL}?page={current_page}'
    headers = {'User-Agent':USER_AGENT}
    request = urllib.request.Request(url_str,None,headers) #The assembled request
    response = urllib.request.urlopen(request)
    content = response.read().decode()

    page_content = BeautifulSoup(content, 'html.parser')

    # find list of cars
    articles = page_content.find_all('article', attrs={"class":"result-tile"})
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
