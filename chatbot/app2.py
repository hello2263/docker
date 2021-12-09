from flask import Flask, jsonify, render_template, request
from flask_restful import Resource, Api, reqparse
from datetime import datetime
from pymongo import MongoClient
from pymongo.cursor import CursorType
import requests, json, time, sys, os, func
global friend, code

app = Flask(__name__)
host = "172.17.0.2"
port = "27017"
mongo = MongoClient(host, int(port), connect=False)
mydb = mongo['alarm']
myweather = mydb['weather']
mysetting = mydb['setting']
friend = {}

def alarm_setting_update():
    func.update_item_one(mongo, {"name":str(friend['name'])}, {"$set": {"local":str(friend['local']), "day":str(friend['day']), "time":str(friend['time']), "content":str(friend['content'])}}, "alarm", "setting")
    print("setting update")

@app.route('/start_alarm', methods=['POST'])
def start_alarm():
    if request.method == 'POST':
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

@app.route('/name', methods=['POST'])
def get_name():
    global user_name
    value = {}
    check = {}
    if request.method == 'POST':
        content = request.get_json()
        content = content['action']['params']['kakao_name']
        friend['name'] = content
        user_data = func.find_item(mongo, {"name":friend['name']}, "alarm", "setting")
        user_check = func.find_item(mongo, {"name":friend['name']}, "alarm", "kakao")
        for i in user_data:
            value = i
        for j in user_check:
            check = j
        print(content + '님이 앱 실행 중')
        if value.get('name') == None:
            if check.get('name') == None:
                dataSend = {
                    "version": "2.0",
                    "template": {
                        "outputs": [
                                {
                                    "basicCard": 
                                        {
                                            "title":"앱을 실행한 이력이 없습니다.",
                                            "buttons": [{
                                                "action":"message",
                                                "label":"알람 설정",
                                                "messageText": "알람 설정"
                                        }]
                                        }
                                }
                                ]
                    }
                }
                return jsonify(dataSend)
            else:
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
            
        else:
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
            
@app.route('/delete', methods=['POST'])
def delete_alarm():
    if request.method == 'POST':
        try:
            mysetting.delete_one({'name':user_name})
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
            print(user_name + '님의 알람 삭제완료')
            return jsonify(dataSend)

        except:
            dataSend = {
                "version": "2.0",
                "template": {
                    "outputs": [
                        {
                            "simpleText":{
                                "text" : "삭제할 알람이 없습니다."
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
        friend['content'] = content['content']
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
