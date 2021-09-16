from flask import Flask, jsonify, request, render_template, redirect, session
from data_accquiring import start_data_accquiring, build_brand_model_relationship
from conf import MAX_NUMBER_OF_DISPLAYED_BRANDS
from apscheduler.schedulers.background import BackgroundScheduler
import car
import brand
import sys
import threading
import json

app = Flask(__name__, template_folder='Templates')

app.secret_key = 'super secret key'
#app.config['SESSION_TYPE'] = 'filesystem'
#session.init_app(app)

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

@app.route('/selectbybrand')
def selectbybrand():
    brands = brand.get_all_brands()
    data = [brand.serialize() for brand in brands]

    return render_template('selectbybrand.html', data=json.dumps(data))

@app.route('/crud')
def crud():
    # get car list
    cars = [car.serialize() for car in car.get_cars_by_filters({})]

    # get brand list
    brands = [brand.serialize() for brand in brand.get_all_brands()]

    # get message
    message = session.pop('message', None)

    # build data object
    data = {
        'cars': cars,
        'brands': brands,
        'message': message
    }
    return render_template('crud.html', data=data)

@app.route('/savecar', methods = ['POST','GET'])
def savecar():
    print(request.form)
    #car_id = request.form['car_id']
    #year = request.form['manufacture_year']
    #brand = request.form['brand']
    #model = request.form['model']
    #mileage = request.form['mileage']
    #price = request.form['price']

    #c = car.Car(car_id, year, brand, model, mileage, price)
    #print(c.serialize())
    #employee = EmployeeModel(employee_id=employee_id, name=name, age=age, position = position)
    #db.session.add(employee)
    #db.session.commit()

    session['message'] = "Car has been saved!"
    return redirect('/crud')
        

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
    app.debug = True
    app.run()