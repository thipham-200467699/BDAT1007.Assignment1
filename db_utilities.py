from pymongo import MongoClient
from pymongo.errors import BulkWriteError
from bson.son import SON
from conf import DB_CONNECTION_STRING


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
        db = self.client.finalproject
        db.cars.drop()
    
    def find_all_cars(self, criteria):
        db = self.client.finalproject
        return db.cars.find(criteria)
    
    def find_one_car(self, criteria):
        db = self.client.finalproject
        return db.cars.find_one(criteria)

    def save_cars_to_db(self, cars):
        db = self.client.finalproject

        if cars and len(cars) > 0:
            try:
                db.cars.insert_many(documents=cars, ordered=False)
            except BulkWriteError as e:
                pass

    def get_car_brand_statistics(self):
        db = self.client.finalproject

        pipeline = [
            {"$group": {"_id": "$brand", "count": {"$sum": 1}}},
            {"$sort": SON([("count", -1)])}
        ]
        return list(db.cars.aggregate(pipeline))

    def get_avg_price_by_brand(self):
        db = self.client.finalproject

        pipeline = [
            {"$group": {"_id": "$brand", "avg_price": {"$avg": "$price"}}},
            {"$sort": SON([("avg_price", -1)])}
        ]
        return list(db.cars.aggregate(pipeline))
    
    def get_avg_price_by_preferred_brand(self, brands):
        db = self.client.finalproject

        pipeline = [
            {"$match": {"brand": {"$in":brands}}},
            {"$group": {"_id": "$brand", "avg_price": {"$avg": "$price"}}},
            {"$sort": SON([("avg_price", 1)])}
        ]
        return list(db.cars.aggregate(pipeline))

    def get_avg_mileage_by_year(self):
        db = self.client.finalproject

        pipeline = [
            {"$group": {"_id": "$year", "avg_mileage": {"$avg": "$mileage"}}},
            {"$sort": SON([("_id", 1)])}
        ]
        return list(db.cars.aggregate(pipeline))
    
    def close_connection(self):
        if self.client:
            self.client.close()