import os, sys, shutil, time
from flask import Flask, request, jsonify, render_template,send_from_directory
import pandas as pd
import joblib
import sqlite3
import csv
from sklearn.ensemble import RandomForestClassifier
import numpy as np
import urllib.request
import json
from geopy.geocoders import Nominatim
import geopy
#geopy.geocoders.options.default_user_agent = "my-application"
app = Flask(__name__)
@app.route("/")
def home():
    # return the homepage
    return render_template("login.html")

@app.route("/signup")
def signup():
    name = request.args.get('username','')
    dob = request.args.get('DOB','')
    sex = request.args.get('Sex','')
    contactno = request.args.get('CN','')
    email = request.args.get('email','')
    martial = request.args.get('martial','')
    password = request.args.get('psw','')

    con = sqlite3.connect('signup.db')
    cur = con.cursor()
    cur.execute("insert into `accounts` (`name`, `dob`,`sex`,`contact`,`email`,`martial`, `password`) VALUES (?, ?, ?, ?, ?, ?, ?)",(name,dob,sex,contactno,email,martial,password))
    con.commit()
    con.close()

    return render_template("login.html")

@app.route("/signin")
def signin():
    mail1 = request.args.get('uname','')
    password1 = request.args.get('psw','')
    con = sqlite3.connect('signup.db')
    cur = con.cursor()
    cur.execute("select `email`, `password` from accounts where `email` = ? AND `password` = ?",(mail1,password1,))
    data = cur.fetchone()

    if data == None:
        return render_template("login.html")

    elif mail1 == data[0] and password1 == data[1]:
        return render_template("index.html")

    
    else:
        return render_template("login.html")
@app.route('/register')
def register():
    return render_template("register.html")

@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/work')
def work():
    return render_template('work.html')

@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/result.html', methods = ['POST'])
def predict():
    rfc = joblib.load('model.sav')
    print('model loaded')

    if request.method == 'POST':

        address = request.form['Location']
        geolocator = Nominatim(user_agent="app")
        location = geolocator.geocode(address,timeout=None)
        print(location.address)
        lat=[location.latitude]
        log=[location.longitude]
        latlong=pd.DataFrame({'latitude':lat,'longitude':log})
        print(latlong)

        DT= request.form['timestamp']
        latlong['timestamp']=DT
        data=latlong
        cols = data.columns.tolist()
        cols = cols[-1:] + cols[:-1]
        data = data[cols]

        data['timestamp'] = pd.to_datetime(data['timestamp'].astype(str), errors='coerce')
        data['timestamp'] = pd.to_datetime(data['timestamp'], format = '%d/%m/%Y %H:%M:%S')
        column_1 = data.iloc[:,0]
        DT=pd.DataFrame({"year": column_1.dt.year,
              "month": column_1.dt.month,
              "day": column_1.dt.day,
              "hour": column_1.dt.hour,
              "dayofyear": column_1.dt.dayofyear,
              "week": column_1.dt.week,
              "weekofyear": column_1.dt.weekofyear,
              "dayofweek": column_1.dt.dayofweek,
              "weekday": column_1.dt.weekday,
              "quarter": column_1.dt.quarter,
             })
        data=data.drop('timestamp',axis=1)
        final=pd.concat([DT,data],axis=1)
        X=final.iloc[:,[1,2,3,4,6,10,11]].values
        my_prediction = rfc.predict(X)
        if my_prediction[0][0] == 1:
            my_prediction='Predicted crime : Act 379-Robbery'
        elif my_prediction[0][1] == 1:
            my_prediction='Predicted crime : Act 13-Gambling'
        elif my_prediction[0][2] == 1:
            my_prediction='Predicted crime : Act 279-Accident'
        elif my_prediction[0][3] == 1:
            my_prediction='Predicted crime : Act 323-Violence'
        elif my_prediction[0][4] == 1:
            my_prediction='Predicted crime : Act 302-Murder'
        elif my_prediction[0][5] == 1:
            my_prediction='Predicted crime : Act 363-kidnapping'
        else:
            my_prediction='Place is safe no crime expected at that timestamp.'



    return render_template('result.html', prediction = my_prediction)


if __name__ == '__main__':
    app.run(debug = True)
