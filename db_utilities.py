from pymongo import MongoClient
from pymongo.errors import BulkWriteError
from conf import DB_CONNECTION_STRING

import uuid


class DbUtiltity:

    def __init__(self):
        self.client = None
        self.connect_to_db()

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.close_connection()

    def connect_to_db(self):
        if not self.client:
            self.client = MongoClient(DB_CONNECTION_STRING)
    
    def drop_cars_collection(self):
        db = self.client.bdat1007assignm1
        db.cars.drop()
    
    def drop_brand_models_collection(self):
        db = self.client.bdat1007assignm1
        db.brand_models.drop()

    def find_brand_models(self):
        db = self.client.bdat1007assignm1

        pipeline = [
            {"$group": { "_id": { "brand": "$brand", "model": "$model" } } }
        ]
        return list(db.cars.aggregate(pipeline))
    
    def save_brand_models(self, brand_models):
        db = self.client.bdat1007assignm1
        if brand_models and len(brand_models) > 0:
            db.brand_models.insert_many(documents=brand_models, ordered=False)
    
    def save_brand_model(self, brand_model):
        db = self.client.bdat1007assignm1
        db.brand_models.insert_one(brand_model)
    
    def find_all_brands(self):
        db = self.client.bdat1007assignm1
        return db.brand_models.find({})
    
    def find_models_by_brand(self, brand):
        db = self.client.bdat1007assignm1

        return db.brand_models.find({"brand":brand})
    
    def find_all_cars(self, criteria):
        db = self.client.bdat1007assignm1
        return db.cars.find(criteria).sort([('_id', -1)])
    
    def find_one_car(self, criteria):
        db = self.client.bdat1007assignm1
        return db.cars.find_one(criteria)

    def save_cars_to_db(self, cars):
        db = self.client.bdat1007assignm1

        if cars and len(cars) > 0:
            try:
                db.cars.insert_many(documents=cars, ordered=False)
            except BulkWriteError as e:
                pass
    
    def save_car(self, car):
        db = self.client.bdat1007assignm1
        db.cars.insert_one(car)
    
    def update_car(self, car):
        db = self.client.bdat1007assignm1
        db.cars.update({'_id':car._id},{'$set':{'year':car.year, 'brand':car.brand, 'model':car.model, 'mileage':car.mileage, 'price':car.price}})

    def delete_car(self, car_id):
        db = self.client.bdat1007assignm1
        db.cars.delete_one({'_id':car_id})

    def get_max_car_id(self):
        db = self.client.bdat1007assignm1
        c = db.cars.find().sort([('_id', -1)]).limit(1)
        return c[0]["_id"]
    
    def close_connection(self):
        if self.client:
            self.client.close()