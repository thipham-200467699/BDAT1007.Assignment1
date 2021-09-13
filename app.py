from flask import Flask, jsonify, request, render_template
from data_accquiring import start_data_accquiring
from conf import MAX_NUMBER_OF_DISPLAYED_BRANDS
from apscheduler.schedulers.background import BackgroundScheduler
import car
import sys
import threading
import time
import atexit

app = Flask(__name__, template_folder='Templates')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    # Get brand statistics
    brand_statistics = car.get_car_brand_statistics()
    data1 = {'Brands':'Count'}
    data1.update(brand_statistics)

    # build final data
    data = {'brand_statistics': data1}

    return render_template('dashboard.html', data=data)

@app.route('/datamodel')
def datamodel():
    return render_template('datamodel.html')

@app.route('/crud')
def crud():
    return render_template('crud.html')

@app.route('/api/v1/cars/importdata', methods=['GET'])
def import_car_data():
    threading.Thread(target=start_data_accquiring).start()
    return "OK", 200

@app.route('/api/v1/cars/all', methods=['GET'])
def get_all_cars():
    cars = car.get_cars_by_filters({})
    return jsonify([c.serialize() for c in cars])

@app.route('/api/v1/cars/<_id>', methods=['GET'])
def get_car_by_id(_id):
    _car = car.get_car_by_id(_id)
    return jsonify(_car.serialize() if _car else {})

@app.route('/api/v1/cars/filter', methods=['GET'])
def get_cars_by_filter():
    criteria = {}
    cars = []
    
    try:
        if 'brand' in request.args:
            car_brand = request.args['brand']
            criteria.update({'brand' : {'$regex': f'.*{car_brand}.*', '$options': 'i'}})

        if 'model' in request.args:
            model = request.args['model']
            criteria.update({'model' : {'$regex': f'.*{model}.*', '$options': 'i'}})

        if 'years' in request.args:
            _year = request.args['years']
            criteria.update({'year' : {"$in":list(map(int, _year.split(',')))}})

        max_mileage = sys.maxsize
        min_mileage = 0
        if 'max_mileage' in request.args:
            max_mileage = int(request.args['max_mileage'])

        if 'min_mileage' in request.args:
            min_mileage = int(request.args['min_mileage'])

        criteria.update({'mileage' : {'$gte': min_mileage, '$lte': max_mileage}})

        max_price = sys.maxsize
        min_price = 0
        if 'max_price' in request.args:
            max_price = int(request.args['max_price'])

        if 'min_price' in request.args:
            min_price = int(request.args['min_price'])

        criteria.update({'price' : {'$gte': min_price, '$lte': max_price}})

        cars = car.get_cars_by_filters(criteria)
    except Exception as e:
        print(e)

    return jsonify([c.serialize() for c in cars])


if __name__ == "__main__":
    app.run()