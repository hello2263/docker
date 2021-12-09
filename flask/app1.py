from flask import Flask, jsonify, render_template, request
from flask_restful import Resource, Api, reqparse
from datetime import datetime
from pymongo import MongoClient
from pymongo.cursor import CursorType
from urllib.request import urlopen
import requests, json, time, sys, os, func

app = Flask(__name__)
host = "172.17.0.2"
port = "27017"
mongo = MongoClient(host, int(port), connect=False)
mydb = mongo['alarm']
mysetting = mydb['setting']
myweather = mydb['weather']
mycode = mydb['code']

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/kakao')
def kakao():
    return render_template('kakao.html')

@app.route('/kakao_owner', methods = ['POST', 'GET'])
def kakao_check_owner():
    if request.method == 'POST':
        code = request.form['code']
        print(code)
        func.kakao_to_friends_get_ownertokens(code)
        user = func.kakao_owner_token()
        func.kakao_friends_update()
        return render_template('kakao_owner.html', user = user)
    else:
        return render_template('kakao_owner.html')

@app.route('/kakao_friends', methods=['GET', 'POST'])
def kakao_friends():
    if request.method == 'POST':
        code = request.form['code']
        print(code)
        kakao_to_friends_get_friendstokens(code)
        user = func.kakao_friends_token()
        return render_template('kakao_friends.html', user = user)
    else:
        return render_template('kakao_friends.html')
    
@app.route('/weather', methods=['GET', 'POST'])
def weather_alarm():
    global select_date
    select_date = func.nowtime()
    weather = set_data_for_weather(select_date)
    return render_template('weather.html', data = weather)

@app.route('/kakao_friend_code', methods=['GET', 'POST'])
def kakao_friend_code():
    global user_kakao_code
    if request.method == 'POST': 
        return render_template('kakao_code.html')
    else:
        args_dict = request.args.to_dict()
        friend_code = args_dict['code']
        print(friend_code)
        kakao_to_friends_get_friendstokens(friend_code)
        func.kakao_friends_token()
        mycode.remove({})
        func.insert_item_one(mongo, {"code":str(friend_code)}, "alarm", "code")
        return render_template('kakao_code.html')

@app.route('/kakao_owner_code', methods=['GET', 'POST'])
def kakao_owner_code():
    global user_kakao_code
    args_dict = request.args.to_dict()
    owner_code = args_dict['code']
    print(owner_code)
    mycode.remove({})
    func.insert_item_one(mongo, {"code":str(owner_code)}, "alarm", "code")
    return render_template('kakao_code.html')

def kakao_to_friends_get_friendstokens(code):
    url = 'https://kauth.kakao.com/oauth/token'
    authorize_code = code
    data = {
        'grant_type':'authorization_code',
        'client_id':'91d3b37e4651a9c3ab0216abfe877a50',
        'redirect_uri':'http://3.35.252.82:5000/kakao_friend_code',
        'code': authorize_code,
        }
    response = requests.post(url, data=data)
    tokens = response.json()
    print(tokens)
    with open("kakao_code_friends_friends.json","w") as fp:
        json.dump(tokens, fp)

def find_local_from_db():
    cursor = func.find_item(mongo, None, "alarm", "local").noCursorTimeout()
    for list in cursor:
        print(list)
        local_name.append(list["city"])
        local_x.append(list["x"])
        local_y.append(list["y"])
    return local_name, local_x, local_y

def set_data_for_weather(time):
    count = 0
    weather = [{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}]
    dict_data = func.find_item(mongo, {"date":time}, "alarm", "weather")
    for i in dict_data:
        j = i['local']
        if j[-1] == '구':
            weather[count] = i
            count += 1
        else:
            break
    return weather

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




