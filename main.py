import requests
import yaml
import urllib
from calculate import *
import time

def config():
    global api
    global msg_id
    global group_id
    configfile = open('config.yaml', 'r', encoding="utf-8")
    data = yaml.load(configfile,Loader=yaml.FullLoader) #load config
    api = data['api'] #get api
    group_id = str(data['group_id']) #get group id
    msg_id = 0 #we don't want a message to be send many times, so we use a set to store the message_id

def get_group_msg():
    qs = [
        'http',
        api,
        '/get_group_msg_history',
        '',
        'group_id=' + group_id,
        ''
    ]
    url = (urllib.parse.urlunparse(qs))
    result = requests.get(url)
    json = result.json()['data']['messages'][19] #get newest message
    msg_id = json['message_id']
    msg = json['message']
    sender_uid = json['sender']['user_id']
    gathering = {
        'msg_id' : str(msg_id),
        'msg' : msg,
        'sender_uid' : str(sender_uid),
    }
    return gathering

def calculate(formula):
    formula_list = formula_format(formula)
    result = final_calc(formula_list)
    return formula + ' = ' + result

def send_msg(msg):
    qs = [
        'http',
        api,
        '/send_msg',
        '',
        'group_id=' + group_id,
        'message=' + msg,
    ]
    url = (urllib.parse.urlunparse(qs))
    print(url)
    result = requests.get(url)
    print(result.text())

def monitor_messages_and_send():
    global msg_id
    data = get_group_msg()
    msg_id_now = data['msg_id']
    sender_uid = data['sender_uid']
    if msg_id_now == msg_id:
        return
    if msg_id_now != msg_id:
        msg_id = msg_id_now
        try:
            result = calculate(data['msg'])
        except:
            print('not a calculating message')
            return
        msg = '[CQ:reply,id=' + msg_id_now + '][CQ:at,qq=' + sender_uid + '][CQ:at,qq=' + sender_uid + '] ' + result
        send_msg(msg)

config()
while True:
    monitor_messages_and_send()
    time.sleep(2)