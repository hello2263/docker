from flask import Flask, jsonify, render_template, request
from flask_restful import Resource, Api, reqparse
from datetime import datetime
from pymongo import MongoClient
from pymongo.cursor import CursorType
import requests, json, time, sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname('__file__')))+"/flask/")
import app1
global friend, code

app = Flask(__name__)
host = "172.17.0.2"
port = "27017"
mongo = MongoClient(host, int(port), connect=False)
mydb = mongo['alarm']
myweather = mydb['weather']
mysetting = mydb['setting']
friend = {}

def update_item_one(mongo, condition=None, update_value=None, db_name=None, collection_name=None):
    result = mongo[db_name][collection_name].update_one(filter=condition, update=update_value, upsert=True)
    return result

@app.route("/")
def home():
    return "Hello, Flask"

def alarm_setting_update():
    update_item_one(mongo, {"name":str(friend['name'])}, {"$set": {"local":str(friend['local']), "day":str(friend['day']), "time":str(friend['time'])}}, "alarm", "setting")
    print("setting update")

@app.route('/experience', methods=['POST'])
def get_experience():
    if request.method == 'POST':
        content = request.get_json()
        dataSend = {
            "version": "2.0",
            "template": {
                "outputs": [
                        {
                            "basicCard": 
                                {
                                    "title":"이 앱에서 알람설정은 처음인가요?",
                                    "buttons": [{
                                        "action":"message",
                                        "label":"처음이다",
                                        "messageText": "처음이다"
                                },
                                {
                                        "action":"message",
                                        "label":"아니다",
                                        "messageText": "아니다"
                                }]
                                }
                        }
                        ]
            }
        }
        return jsonify(dataSend)

@app.route('/code', methods=['POST'])
def get_code():
    if request.method == 'POST':
        content = request.get_json()
        content = content['action']['detailParams']['code']['origin']
        start = int(content.find('code')) + 5
        code = content[start:]
        print(code)
        dataSend = {
            "version": "2.0",
            "template": {
                "outputs": [
                        {
                            "basicCard": 
                                {
                                    "title":"코드가 입력됐습니다.",
                                    "buttons": [{
                                        "action":"message",
                                        "label":"사용자 이름 입력",
                                        "messageText": "이름 입력"
                                }]
                                }
                        }
                        ]
            }
        }
        app1.kakao_to_friends_get_friendstokens(code)
        app1.kakao_friends_token()
        app1.kakao_friends_check()
        return jsonify(dataSend)

@app.route('/name', methods=['POST'])
def get_name():
    global user_name
    if request.method == 'POST':
        content = request.get_json()
        print(content)
        content = content['action']['params']['kakao_name']
        friend['name'] = content
        print(content)
        try:
            user_data = app1.find_item(mongo, {"name":friend['name']}, "alarm", "setting")
            user_name = friend['name']
            dataSend = {
                "version": "2.0",
                "template": {
                    "outputs": [
                            {
                                "basicCard": 
                                    {
                                        "title":"설정된 알람이 있습니다. 무엇을 하고 싶나요?",
                                        "buttons": [{
                                            "action":"message",
                                            "label":"알람 생성/수정",
                                            "messageText": "알람 생성/수정"
                                    },
                                    {
                                            "action":"message",
                                            "label":"알람 삭제",
                                            "messageText": "알람 삭제"
                                    }]
                                    }
                            }
                            ]
                }
            }
            return jsonify(dataSend)
        except:
            dataSend = {
                "version": "2.0",
                "template": {
                    "outputs": [
                            {
                                "basicCard": 
                                    {
                                        "title":"설정된 알람이 없습니다. 무엇을 하고 싶나요?",
                                        "buttons": [{
                                            "action":"message",
                                            "label":"알람 생성/수정",
                                            "messageText": "알람 생성/수정"
                                    },
                                    {
                                            "action":"message",
                                            "label":"알람 삭제",
                                            "messageText": "알람 삭제"
                                    }]
                                    }
                            }
                            ]
                }
            }
            return jsonify(dataSend)

@app.route('/delete', methods=['POST'])
def delete_alarm():
    if request.method == 'POST':
        mysetting.remove({'name':user_name})
        dataSend = {
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleText":{
                            "text" : "알람이 삭제됐습니다."
                        }
                    }
                ]
            }
        }
        return jsonify(dataSend)

@app.route('/set_time', methods=['POST'])
def set_time():
    if request.method == 'POST':
        content = request.get_json()
        content = content['action']['params']
        friend['local'] = content['local']
        friend['day'] = content['day']
        friend['time'] = content['time']
        dataSend = {
            "version": "2.0",
            "template": {
                "outputs": [
                        {
                            "basicCard": 
                                {
                                    "title":"알람 설정이 완료됐습니다.",
                                }
                            
                        }
                        ]
            }
        }
        print(friend)
        alarm_setting_update()
        return jsonify(dataSend)
