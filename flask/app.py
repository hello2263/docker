from flask import Flask, render_template
from flask_restful import Resource, Api, reqparse


app = Flask(__name__)
api = Api(app)

@app.route('/')
def render_home():
    return render_template('home.html')

if __name__ == '__main__':
    print('testing')
    app.run(host='0.0.0.0', port=5000)

