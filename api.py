import TLHCore
import HCHScore
import CHGSHore
from flask import Flask, request
import json
import configparser

app = Flask(__name__)

config = configparser.ConfigParser()
config.read('config.ini',encoding="utf8")
host = config.get('General', 'host')
port = config.getint('General', 'port')

@app.route('/TLHC', methods=['GET'])
def TLHS():
    client_data = request.form
    try:
        server_data = TLHCore.get(client_data['account'], client_data['password'], client_data['mode'])
    except ValueError:
        return 'Account or password Error!'
    return server_data if isinstance(server_data, str) else json.dumps(server_data, ensure_ascii=False)

@app.route('/HCHS', methods=['GET'])
def HCHS():
    client_data = request.form
    try:
        server_data = HCHScore.get(client_data['account'], client_data['password'], client_data['mode'])
    except ValueError:
        return 'Account or password Error!'
    return server_data if isinstance(server_data, str) else json.dumps(server_data, ensure_ascii=False)

@app.route('CHGSH', methods=['GET'])
def CHGSH():
    client_data = request.form
    try:
        server_data = CHGSHore.get(client_data['account'], client_data['password'], client_data['mode'])
    except ValueError:
        return 'Account or password Error!'
    return server_data if isinstance(server_data, str) else json.dumps(server_data, ensure_ascii=False)
if __name__ == '__main__':
    app.run(host=host, port=port)