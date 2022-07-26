import websocket
import yaml
from calculate import *
import re
import json
import math
from everydaywechat_control.weather.sojson import *

def config():
    global ws_url
    global enabled_groups
    configfile = open('config.yaml', 'r', encoding="utf-8")
    data = yaml.load(configfile,Loader=yaml.FullLoader) #load config
    ws_url = data['ws_url'] #ws address
    enabled_groups = data['enabled_groups'] #enable groups

def calculate_num(formula):
    max = math.factorial(1600) #max value, or tencent won't let you to send this out
    if formula.__contains__('!'):
        formula_try = re.sub('!', '', formula) #still because of max value, we need to check if the value is too big, but we do this before calculation
        if int(formula_try) > 1600:
            return '数字超过可发送范围！'
    if formula.__contains__('！'): #same as above
        formula_try = re.sub('！', '', formula)
        if int(formula_try) > 1600:
            return '数字超过可发送范围！'
    if formula.__contains__('='): #same as above
        formula = re.sub('=', '', formula)  #remove =
    formula_list = formula_format(formula) #format the formula
    result = final_calc(formula_list) #calculate the formula and get the result
    return formula + '=' + result

def calculate(formula):
    try:
        result = calculate_num(formula)
    except:
        result_after =  {
            'success' : 'False',
        }
        return result_after

    result_after = {
        'success' : 'True',
        'result' : result,
    }
    return result_after

def weather(message):
    message = message.split()
    result = {
        'success' : 'True',
    }
    if message[0] == '/天气':
        city_name = message[1]
        result_weather = get_sojson_weather(city_name, False)
        if result_weather != None:
            result['result'] = result_weather
        else:
            result['result'] = '查询失败'
    else:
        result['success'] = 'False'
    return result
    


def ws_connect():
    global ws
    def on_message(ws, message):
        function(message) #call function to handle message
    def on_error(ws, error):
        print(error)
    def on_close(ws):
        print("### closed ###")
    ws = websocket.WebSocketApp(ws_url, on_message=on_message, on_error=on_error, on_close=on_close) #connect to cqhttp_ws
    ws.run_forever()

def send_msg(info):
    send = {
    "action": "send_msg",
    "params": {
        "message": info['msg']
    },
    }
    if info['is_group'] == 'False':
        send['params']["user_id"] =  info['sender_uid']
    else:
        send['params']['group_id'] = info['group_id']
    print(json.dumps(send))
    ws.send(json.dumps(send))


def function(message):
    if message.__contains__('"post_type":"meta_event"'): 
        return #no need to do anything for this
    elif message.__contains__('"post_type":"message"'):
        func_msg(message) #call func_msg to handle message
    elif message.__contains__('"post_type":"notice"'):
        notice(message)
    elif message.__contains__('"post_type":"request"'):
        request(message)

def func_msg(message):
    message = json.loads(message)
    if message['message_type'] == 'private':
        func_private(message) # two different functions to handle different type of chats
    if message['message_type'] == 'group':
        func_group(message)


def func_group(message):
    msg_id = str(message['message_id'])
    msg = message['message']
    sender_uid = str(message['sender']['user_id'])
    group_id = str(message['group_id']) #only for group chat
    if int(group_id) not in enabled_groups:
        return
    info = {
        'is_group': 'True',
        'group_id': group_id,
        'msg_id' : msg_id,
        'sender_uid' : sender_uid,
    }
    result_calc = calculate(msg) #try to calculate the result
    if result_calc['success'] == 'True':
        message = '[CQ:reply,id=' + msg_id + '][CQ:at,qq=' + sender_uid + '][CQ:at,qq=' + sender_uid + '] ' + result_calc['result']
        info['msg'] = message
        send_msg(info)
    else:
        pass
    weather_result = weather(msg)
    if weather_result['success'] == 'True':
        message = '[CQ:reply,id=' + msg_id + '][CQ:at,qq=' + sender_uid + '][CQ:at,qq=' + sender_uid + '] ' + weather_result['result']
        info['msg'] = message
        send_msg(info)
    else:
        pass
    
    
def func_private(message):
    msg_id = str(message['message_id'])
    msg = message['message']
    sender_uid = str(message['sender']['user_id'])
    info = {
        'is_group': 'False',
        'msg_id' : msg_id,
        'sender_uid' : sender_uid,
    }
    result_calc = calculate(msg) #try to calculate the result'
    if result_calc['success'] == 'True':
        message = '[CQ:reply,id=' + msg_id + ']'  + result_calc['result']
        info['msg'] = message
        send_msg(info)
    else:
        pass
    weather_result = weather(msg)
    if weather_result['success'] == 'True':
        message = '[CQ:reply,id=' + msg_id + ']'  + weather_result['result']
        info['msg'] = message
        send_msg(info)
    else:
        pass


def request(message):
    print('请求！')


def notice(message):
    print('通知！')


config()
ws_connect()