import TLHCore
import HCHScore
import CHGSHore
from flask import Flask, request
import json
import configparser
import ssl

config = configparser.ConfigParser()
config.read('config.ini',encoding="utf8")
host = config.get('General', 'host')
port = config.getint('General', 'port')
SSL = config.getboolean('SSL', 'enable')
if SSL:
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.load_cert_chain(config.get('SSL', 'cert'), config.get('SSL', 'key'))

app = Flask(__name__)

def server(client_data, school):
    client_data = request.form
    server_datas = {
        'TLHC': TLHCore,
        'HCHS': HCHScore,
        'CHGSH': CHGSHore
    }
    try:
        server_data = server_datas[school].get(client_data['account'], client_data['password'], client_data['mode'])
    except ValueError:
        return 'Account or password Error!'
    return server_data if isinstance(server_data, str) else json.dumps(server_data, ensure_ascii=False)

@app.route('/TLHC', methods=['POST'])
def TLHC():
    return server(request.form, 'TLHC')

@app.route('/HCHS', methods=['POST'])
def HCHS():
    return server(request.form, 'HCHS')

@app.route('/CHGSH', methods=['POST'])
def CHGSH():
    return server(request.form, 'CHGSH')
    
if __name__ == '__main__':
    if SSL:
        app.run(host=host, port=port, ssl_context=context)
    else:
        app.run(host=host, port=port)