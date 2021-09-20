from db_utilities import DbUtiltity
import pandas as pd

def start_import_csv():
    # Read data from csv file
    df1 = pd.read_csv('cars.csv')
    cars = []
    for index, row in df1.iterrows():
        cars.append({'_id': str(row['ID'])
                    , 'year': row['Year']
                    , 'brand': row['Brand']
                    , 'model': row['Model']
                    , 'mileage': int(row['Mileage'])
                    , 'price': int(row['Price'])})
    
    # Save rows to database
    with DbUtiltity() as db_util:
        try:
            db_util.connect_to_db()
            db_util.drop_cars_collection()

            if len(cars) > 0:
                db_util.save_cars_to_db(cars)
        except Exception as e:
            print(e)
    
    # Build Brand-Model relationship (One to many)
    build_brand_model_relationship()


def build_brand_model_relationship():
    with DbUtiltity() as db_util:
        db_util.connect_to_db()
        db_util.drop_brand_models_collection()

        brand_model_pairs = [id['_id'] for id in db_util.find_brand_models()]
        db_util.save_brand_models(brand_model_pairs)