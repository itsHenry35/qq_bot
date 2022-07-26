import websocket
import yaml
from calculate import *
import re
import json
import math

a=0

def ws_connect():
    global ws
    websocket.enableTrace(True)
    def on_message(ws, message):
        yeah()
    def on_error(ws, error):
        print(error)
    def on_close(ws):
        print("### closed ###")
    ws = websocket.WebSocketApp('ws://127.0.0.1:18080', on_message=on_message, on_error=on_error, on_close=on_close) #connect to cqhttp_ws
    ws.run_forever()

def send_msg(info):
    global ws
    send = {
    "action": "send_msg",
    "params": {
        "message": info['msg']
    },
    }
    send['params']['group_id'] = info['group_id']
    print(json.dumps(send))
    ws.send(json.dumps(send))

def yeah():
    global a
    if a == 0:
        info = {
            'is_group': 'True',
            'group_id': 258545624
            }
        info['msg'] = 'yeah'
        send_msg(info)
        a = 1
ws_connect()
