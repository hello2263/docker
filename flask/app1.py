from flask import Flask, jsonify, render_template, request
from flask_restful import Resource, Api, reqparse
from datetime import datetime
from pymongo import MongoClient
from pymongo.cursor import CursorType
from urllib.request import urlopen
import requests, json, time, sys, os

app = Flask(__name__)
host = "172.17.0.2"
port = "27017"
mongo = MongoClient(host, int(port), connect=False)
mydb = mongo['alarm']
mysetting = mydb['setting']
myweather = mydb['weather']

def insert_item_one(mongo, data, db_name=None, collection_name=None):
    result = mongo[db_name][collection_name].insert_one(data).inserted_id
    return result

def update_item_one(mongo, condition=None, update_value=None, db_name=None, collection_name=None):
    result = mongo[db_name][collection_name].update_one(filter=condition, update=update_value, upsert=True)
    return result

def find_item(mongo, condition=None, db_name=None, collection_name=None):
    result = mongo[db_name][collection_name].find(condition, {"_id":False})
    return result

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
        kakao_to_friends_get_ownertokens(code)
        kakao_owner_token()
        user = kakao_owner_check()
        kakao_friends_update()
        return render_template('kakao_owner.html', user = user)
    else:
        return render_template('kakao_owner.html')

@app.route('/kakao_friends', methods=['GET', 'POST'])
def kakao_friends():
    if request.method == 'POST':
        code = request.form['code']
        print(code)
        kakao_to_friends_get_friendstokens(code)
        kakao_friends_token()
        user = kakao_friends_check()
        return render_template('kakao_friends.html', user = user)
    else:
        return render_template('kakao_friends.html')
    
@app.route('/weather', methods=['GET', 'POST'])
def weather_alarm():
    global select_date
    select_date = nowtime()
    weather = set_data_for_weather(select_date)
    return render_template('weather.html', data = weather)

def kakao_owner_check():
    with open("/home/ec2-user/bot/kakao_code_friends_owner.json","r") as fp:
        tokens = json.load(fp)
    url="https://kapi.kakao.com/v2/user/me"
    headers={"Authorization" : "Bearer " + tokens["access_token"]}
    response = requests.post(url, headers=headers)
    print(response.text)
    print("kakao_owner_check_finish")
    return response.text

def kakao_owner_token():
    with open("/home/ec2-user/bot/kakao_code_friends_owner.json","r") as fp:
        tokens = json.load(fp)
    url="https://kapi.kakao.com/v1/user/access_token_info"
    headers={"Authorization" : "Bearer " + tokens["access_token"]}
    response = requests.post(url, headers=headers)
    print(response.text)
    print("kakao_owner_token_finish")
    return response.text

def kakao_to_friends_get_ownercode():
    url = 'https://kauth.kakao.com/oauth/authorize?client_id=91d3b37e4651a9c3ab0216abfe877a50&redirect_uri=https://3.34.129.77/kakao_friend&response_type=code&scope=talk_message,friends'
    responses = requests.get(url)
    f = urlopen(url)
    data = f.read()
    print(responses._content)
    return code

def kakao_to_friends_get_ownertokens(code):
    url = 'https://kauth.kakao.com/oauth/token'
    authorize_code = code
    data = {
        'grant_type':'authorization_code',
        'client_id':'91d3b37e4651a9c3ab0216abfe877a50',
        'redirect_uri':'https://3.34.129.77/kakao_friend',
        'code': authorize_code,
        }
    response = requests.post(url, data=data)
    tokens = response.json()
    print(tokens)
    with open("/home/ec2-user/bot/kakao_code_friends_owner.json","w") as fp:
        json.dump(tokens, fp)

def kakao_to_friends_get_friendstokens(code):
    url = 'https://kauth.kakao.com/oauth/token'
    authorize_code = code
    data = {
        'grant_type':'authorization_code',
        'client_id':'91d3b37e4651a9c3ab0216abfe877a50',
        'redirect_uri':'https://3.34.129.77/kakao_friend',
        'code': authorize_code,
        }
    response = requests.post(url, data=data)
    tokens = response.json()
    print(tokens)
    with open("kakao_code_friends_friends.json","w") as fp:
        json.dump(tokens, fp)

def kakao_friends_token():
    with open("./kakao_code_friends_friends.json","r") as fp:
        tokens = json.load(fp)
    url="https://kapi.kakao.com/v1/user/access_token_info"
    headers={"Authorization" : "Bearer " + tokens["access_token"]}
    response = requests.post(url, headers=headers)
    print(response.text)
    return response.text
    
def kakao_friends_check():
    with open("kakao_code_friends_friends.json","r") as fp:
        tokens = json.load(fp)
    url="https://kapi.kakao.com/v2/user/me"
    headers={"Authorization" : "Bearer " + tokens["access_token"]}
    response = requests.post(url, headers=headers)
    print(response.text)
    return response.text
    
def kakao_friends_update():
    with open("kakao_code_friends_owner.json","r") as fp:
        tokens = json.load(fp)
    friend_url = "https://kapi.kakao.com/v1/api/talk/friends"
    headers={"Authorization" : "Bearer " + tokens["access_token"]}
    result = json.loads(requests.get(friend_url, headers=headers).text)
    friends_list = result.get("elements")
    try:
        for friend in friends_list:
            update_item_one(mongo, {"uuid":str(friend['uuid'])}, {"$set": {"id":str(friend['id']), "name":str(friend['profile_nickname']), "image":str(friend['profile_thumbnail_image'])}}, "alarm", "kakao")
            print(friend['profile_nickname']+"success")
    except:
        print('friends_update fail')

def find_local_from_db():
    cursor = find_item(mongo, None, "alarm", "local").noCursorTimeout()
    for list in cursor:
        print(list)
        local_name.append(list["city"])
        local_x.append(list["x"])
        local_y.append(list["y"])
    return local_name, local_x, local_y

def nowtime():
    now = datetime.now()
    if now.month < 10:
        today_month = '0'+str(now.month)
    else:
        today_month = str(now.month) 
    if now.day < 10:
        today_day = '0'+str(now.day)
    else:
        today_day = str(now.day)
    if now.hour < 10:
        today_hour = '0'+str(now.hour)
    else:
        today_hour = str(now.hour)
    today_date = str(now.year)+today_month+today_day
    today_time = today_hour+'00'
    return str(today_date + '-' + today_time)

def set_data_for_weather(time):
    count = 0
    weather = [{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}]
    dict_data = find_item(mongo, {"date":time}, "alarm", "weather")
    for i in dict_data:
        weather[count] = i
        count += 1
    return weather

@app.route('/faq', methods = ['GET', "POST"])
def render_message_send():
    if request.method == 'POST':
        nick = request.form['nick']
        msg = request.form['msg']
        now_date = nowtime()[:-5]
        try:
            insert_item_one(mongo, {"date":now_date, "user":nick, 'faq':msg}, "alarm", "faq")
            print("faq insert")
            return render_template('faq.html')
        except:
            print('error')
            return render_template('faq.html')
    else:
        return render_template('faq.html')




