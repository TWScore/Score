import TLHCore
import HCHScore
import CHGSHore
import falcon
import json

def string_to_dict(data):
    _x = {}
    for i in data.split('&'):
        a = i.split('=')
        _x.update({a[0]:a[1]})
    return _x

class School:
    def __init__(self, lib):
        self.lib=lib
    def on_post(self, req, resp):
        client_data = string_to_dict(req.stream.read().decode('utf-8'))
        try:
            server_data = self.lib.get(client_data['account'], client_data['password'], client_data['mode'])
            resp.body = server_data if isinstance(server_data, str) else json.dumps(server_data, ensure_ascii=False)
        except ValueError:
            resp.body = 'Account or password Error!'

api = falcon.API()
api.add_route('/HCHS', School(HCHScore))
api.add_route('/TLHC', School(TLHCore))
api.add_route('/CHGSH', School(CHGSHore))