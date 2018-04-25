from flask import Flask, render_template, request, jsonify
import base64
import os
from StreamCipher import StreamCipher

app = Flask(__name__)

@app.route('/')
def home():
    return app.send_static_file('index.html')

if __name__ == '__main__':
    # app_theft_checker_2()
    app.run(debug=True, host='127.0.0.1',port=8080,use_reloader=True)