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
        # print(content)
        dataSend = {
            "version": "2.0",
            "template": {
                "outputs": [
                        {
                            "basicCard": 
                                {
                                    "title":"알람설정을 해본적이?",
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
        # print(content)
        content = content['action']['detailParams']['code']['origin']
        print(content)
        if content[0:4] == u"code":
            code = content[5:]
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
        else :
            dataSend = {
                "version": "2.0",
                "template": {
                    "outputs": [
                        {
                            "simpleText":{
                                "text" : "코드가 올바르지 않습니다."
                            }
                        }
                    ]
                }
            }
            return jsonify(dataSend)

@app.route('/name', methods=['POST'])
def get_name():
    if request.method == 'POST':
        content = request.get_json()
        content = content['action']['params']['kakao_name']
        friend['name'] = content
        print(content)
        dataSend = {
            "version": "2.0",
            "template": {
                "outputs": [
                        {
                            "basicCard": 
                                {
                                    "title":"어떤 기능을 사용하고 싶나요?",
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
