from flask import Flask, render_template, request, jsonify, redirect
import base64
import os
from StreamCipher import StreamCipher
import sqlite3

app = Flask(__name__, template_folder='static')

@app.route('/initialize', methods = ['GET'])
def initialize():
    try:
        conn = sqlite3.connect('streamcipher.db')
        conn.execute('CREATE TABLE data (id INTEGER PRIMARY KEY, nonce TEXT, ctext TEXT, key TEXT)')
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
        decrypted_data = instance.decrypt(encrypted_data)
        print("encrypted data: {}".format(encrypted_data))
        print("decrypted data: {}".format(decrypted_data))
        with sqlite3.connect("streamcipher.db") as con:
            cur = con.cursor()
            query = "INSERT INTO data('nonce', 'ctext', 'key') VALUES('" + base64.urlsafe_b64encode(encrypted_data[0]) + "','" + base64.urlsafe_b64encode(encrypted_data[1].encode('latin-1')) + "','" + base64.urlsafe_b64encode(key) + "')"
            print(query)
            cur.execute(query)
        return redirect('/encryptions')
    except Exception as e:
        print("Exception. Reason: {}".format(e))
        return redirect('/error')

@app.route('/encryptions', methods = ['GET'])
def fetch():
    with sqlite3.connect("streamcipher.db") as con:
        cur = con.cursor()
        values = cur.execute('SELECT nonce, ctext, key, id FROM data')
        print("Encrypted values: ")
        dv = list()
        for val in values:
            print(val)
            temp = dict()
            instance = StreamCipher(base64.urlsafe_b64decode(val[2].encode('utf-8')))
            tup = list()
            tup.append(base64.urlsafe_b64decode(val[0].encode('utf-8')))
            tup.append(base64.urlsafe_b64decode(val[1].encode('utf-8')))
            decrypted_data = instance.decrypt(tup)
            temp['nonce'] = val[0]
            temp['ctext'] = val[1]
            temp['id'] = val[3]
            dv.append(temp)
            print("Decrypted data: ")
            print(decrypted_data)
    print("Final values to send: ")
    print(dv)
    return render_template('values.html', summary=dv)

@app.route('/decrypt', methods = ['GET'])
def decrypt_with_id():
    try:
        with sqlite3.connect("streamcipher.db") as con:
            cur = con.cursor()
            values = cur.execute('SELECT nonce, ctext, key, id FROM data WHERE id = ' + request.args.get('id'))
            print("Encrypted values: ")
            dv = dict()
            for val in values:
                print(val)
                instance = StreamCipher(base64.urlsafe_b64decode(val[2].encode('utf-8')))
                tup = list()
                tup.append(base64.urlsafe_b64decode(val[0].encode('utf-8')))
                tup.append(base64.urlsafe_b64decode(val[1].encode('utf-8')))
                decrypted_data = instance.decrypt(tup)
                print("Decrypted data: ")
                print(decrypted_data)
                dv['nonce'] = val[0]
                dv['ctext'] = val[1]
                dv['val'] = decrypted_data
        return render_template('decrypted.html', summary=dv)
    except Exception as e:
        print("Exception in //encryptions. Reason: {}".format(e))   
        return redirect('/error')

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1',port=8080,use_reloader=True)
