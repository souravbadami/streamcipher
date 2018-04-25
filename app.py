from flask import Flask, render_template, request, jsonify, redirect
import base64
import os
from StreamCipher import StreamCipher
import sqlite3

app = Flask(__name__)

@app.route('/initialize', methods = ['GET'])
def initialize():
    try:
        conn = sqlite3.connect('streamcipher.db')
        conn.execute('CREATE TABLE data (value TEXT)')
        conn.close()
        print("Database initialized!")
        return redirect('/')
    except Exception as e:
        print("Database initialization failed! Reason: {}".format(e))
        return redirect('/error')

@app.route('/')
def home():
    return app.send_static_file('index.html')

@app.route('/error')
def error():
    return app.send_static_file('error.html')

@app.route('/save', methods = ['POST'])
def save():
    try:
        val = request.form['value']
        key = base64.urlsafe_b64encode(os.urandom(16))
        instance = StreamCipher(key)
        print("key: {}".format(key))
        print("unencrypted data: {}".format(val))
        encrypted_data = instance.encrypt(val.encode('ascii'))
        print("encrypted data: {}".format(encrypted_data))
        with sqlite3.connect("streamcipher.db") as con:
            cur = con.cursor()
            query = "INSERT INTO data('value') VALUES('" + encrypted_data + "')"
            print(query)
            cur.execute(query)
        return redirect('/encryptions')
    except Exception as e:
        print("Exception. Reason: {}".format(e))
        return redirect('/error')

@app.route('/encryptions', methods = ['GET'])
def fetch():
    try:
        with sqlite3.connect("streamcipher.db") as con:
            cur = con.cursor()
            values = cur.execute('SELECT value FROM data')
            print("Encrypted values: ")
            for val in values:
                print(val)
        return app.send_static_file('values.html')
    except Exception as e:
        redirect('/error')
        print("Exception. Reason: {}".format(e))   

if __name__ == '__main__':
    # app_theft_checker_2()
    app.run(debug=True, host='127.0.0.1',port=8080,use_reloader=True)