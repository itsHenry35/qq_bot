import requests
import yaml
import urllib
from calculate import *
import time
import re

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
    num = 0
    url = (urllib.parse.urlunparse(qs))
    result = requests.get(url)
    json = result.json()['data']['messages'] #get newest message
    num = len(json)
    json = json[num-1]
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
    max = math.factorial(1600)
    if formula.__contains__('!'):
        formula_try = re.sub('!', '', formula)
        if int(formula_try) > 1600:
            return 'Value too big!'
    if formula.__contains__('！'):
        formula_try = re.sub('！', '', formula)
        if int(formula_try) > 1600:
            return 'Value too big!'
    formula = re.sub('=', '', formula) 
    formula_list = formula_format(formula)
    result = final_calc(formula_list)
    if int(result) > max:
        return 'Value too big!'
    else:
        return formula + '=' + result

def send_msg(msg):
    msg=urllib.parse.quote(msg)
    qs = [
        'http',
        api,
        '/send_msg',
        '',
        'group_id=' + group_id + '&message=' + msg + '',
        ''
    ]
    url = urllib.parse.urlunparse(qs)
    print(url)
    result = requests.get(url)
    print(result)
    

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
        print(msg)
        send_msg(msg)

config()
while True:
    try:
        monitor_messages_and_send()
    except:
        time.sleep(2)
    time.sleep(0.5)