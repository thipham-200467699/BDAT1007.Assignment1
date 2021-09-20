from flask import Flask, jsonify, request, render_template, redirect, session
from data_accquiring import start_import_csv
import car
import brand
import threading
import json

app = Flask(__name__, template_folder='Templates')

app.secret_key = 'super secret key'

@app.route('/')
def index():
    return render_template('index.html')


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
    car_id = request.form['car_id']
    year = request.form['manufacture_year']
    brand = request.form['brand']
    model = request.form['model']
    mileage = int(request.form['mileage'], 10)
    price = int(request.form['price'], 10)

    if car_id:
        c = car.Car(car_id, year, brand, model, mileage, price)
        car.update_car(c)
        session['message'] = "The car has been updated!"
    else:
        c = car.Car(car.get_next_car_id(), year, brand, model, mileage, price)
        car.create_car(c)
        session['message'] = "The car has been created!"

    return redirect('/crud')


@app.route('/deletecar', methods = ['POST','GET'])
def deletecar():
    car_id = request.form['deleted_car_id']

    car.delete_car(car_id)

    session['message'] = "The car has been deleted!"
    return redirect('/crud')


@app.route('/api/v1/cars/importdata', methods=['GET'])
def import_car_data():
    threading.Thread(target=start_import_csv).start()
    return "OK", 200


if __name__ == "__main__":
    app.debug = True
    app.run()