from flask import Flask, jsonify, render_template, request
from flask_restful import Resource, Api, reqparse
from datetime import datetime
from pymongo import MongoClient
from pymongo.cursor import CursorType
from urllib.request import urlopen
import requests, json, time, sys, os, func

app = Flask(__name__)
host = "172.17.0.4"
port = "27017"
mongo = MongoClient(host, int(port), connect=False)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/weather/<user_date>', methods=['GET', 'POST'])
def weather_user_gui(user_date):
    global select_date
    ctime, count = count_time()
    weather = set_data_for_weather(user_date)
    return render_template('weather.html', data = weather, date = user_date, time = ctime, count = count)

@app.route('/weather', methods=['GET', 'POST'])
def weather_gui():
    global select_date
    ctime, count = count_time()
    select_date = func.nowtime()
    weather = set_data_for_weather(select_date)
    return render_template('weather.html', data = weather, date = select_date, time = ctime, count = count)


@app.route('/kakao_friend_code', methods=['GET', 'POST'])
def kakao_friend_code():
    if request.method == 'POST': 
        return render_template('kakao_code.html')
    else:
        args_dict = request.args.to_dict()
        friend_code = args_dict['code']
        func.kakao_to_friends_get_friendstokens(friend_code)
        # func.kakao_owner_token()
        # kakao_to_friends_get_refreshtokens()
        func.kakao_friends_token()
        # kakao_to_friends_get_friendrefreshtokens()
        print('a')
        func.kakao_friend_get_data()
        print('b')
        func.delete_item_many(mongo, {}, "alarm", "code")
        func.insert_item_one(mongo, {"code":str(friend_code)}, "alarm", "code")
        # func.kakao_friends_update()
        return render_template('kakao_code.html')

@app.route('/kakao_owner_code', methods=['GET', 'POST'])
def kakao_owner_code():
    args_dict = request.args.to_dict()
    owner_code = args_dict['code']
    func.delete_item_many(mongo, {}, "alarm", "code")
    func.insert_item_one(mongo, {"code":str(owner_code)}, "alarm", "code")
    return render_template('kakao_code.html')

@app.route('/faq', methods = ['GET', "POST"])
def render_message_send():
    if request.method == 'POST':
        nick = request.form['nick']
        msg = request.form['msg']
        now_date = func.nowtime()[:-5]
        try:
            insert_item_one(mongo, {"date":now_date, "user":nick, 'faq':msg}, "alarm", "faq")
            print("faq insert")
            return render_template('faq.html')
        except:
            print('error')
            return render_template('faq.html')
    else:
        return render_template('faq.html')

def find_local_from_db():
    cursor = func.find_item(mongo, None, "alarm", "local").noCursorTimeout()
    for list in cursor:
        local_name.append(list["city"])
        local_x.append(list["x"])
        local_y.append(list["y"])
    return local_name, local_x, local_y

def set_data_for_weather(time):
    count = 0
    weather = [{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}]
    dict_data = func.find_item(mongo, {"date":time}, "alarm", "weather")
    for i in dict_data:
        j = i['local']
        if j[-1] == '구':
            weather[count] = i
            count += 1
        else:
            break
    return weather

def count_time():
    flag = 2
    count = 0
    ctime = []
    date = set_date_for_api()
    date = date[:-2] + '00'
    time_data = func.find_item(mongo, {"local":'강남구', 'date':{"$gte":date}}, "alarm", "weather")
    for i in time_data:
        if flag == 2:
            ctime.append(i)
            count += 1
            flag = 0
        else:
            flag += 1
    return ctime, count

def set_date_for_api(): 
    global today_time, today_date, now
    now = datetime.now()
    today_time = int(str(now.hour)+str(now.minute))
    today_day = now.day
    if today_time < 215:
        today_day -= 1
        today_time = '2330'
    elif today_time < 515:
        today_time = '0230'
    elif today_time < 815:
        today_time = '0530'
    elif today_time < 1115:
        today_time = '0830'
    elif today_time < 1415:
        today_time = '1130'
    elif today_time < 1715:
        today_time = '1430'
    elif today_time < 2015:
        today_time = '1730'
    elif today_time < 2315:
        today_time = '2030'
    else:
        today_time = '2330'   

    if now.month < 10:
        today_month = '0'+str(now.month)
    else:
        today_month = str(now.month)

    if today_day < 10:
        today_day = '0'+str(today_day)
    else:
        today_day = str(today_day)
    today_date = str(now.year)+today_month+today_day
    return today_date + '-' + today_time 






