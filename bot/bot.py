from flask import jsonify, Response, Blueprint, current_app, request
import json
import requests
import os
import hmac
import hashlib
import pprint
import time
import math
import urllib.parse
import random

# ssh -R igetmad:80:localhost:5000 serveo.net

# Register app bp
igetmad = Blueprint('bot', __name__)

url_general = 'https://hooks.slack.com/services/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'
json_headers = {'Content-type': 'application/json'}

slack_api_url = 'https://slack.com/api/'
bresson_headers = 'Content-type: application/x-www-form-urlencoded'

event = dict()


def slack_api_call(method, token=os.getenv('SLACK_OAUTH_TOKEN'), **kwargs):
    request_url=slack_api_url+method+"?token="+token
    for key, value in kwargs.items():
        request_url+="&"+key+"="+urllib.parse.quote(value)
    print(request_url)
    r = requests.post(request_url)
    pprint.pprint(r.json())
    return (r.status_code, r.json())


def verify_slack_request(request):
    # build personal signature to hash
    timestamp=request.headers.get('X-Slack-Request-Timestamp')
    body=request.get_data().decode('utf-8')
    signature_base_string='v0:'+timestamp+':'+body
    signature = "v0="+hmac.new(os.getenv('SLACK_SIGNING_SECRET').encode(), msg=signature_base_string.encode(), digestmod=hashlib.sha256).hexdigest()

    # get slack signature
    slack_signature = request.headers.get('X-Slack-Signature')

    # compare signatures to authentify request
    if signature == slack_signature:
        print('request authentified from slack')
        return True
    else:
        print('request NOT authentified')
        return False

def mention_user(user_id):
    return "<@"+user_id+">"


def coffee_break(user_id):
    interactive = {
        "text": "Hello "+mention_user(user_id)+", tu en peux plus ? :exploding_head: \n C'est bien normal, il faut souffler de temps en temps ! ",
        "attachments": [
            {
                "text": "Ca te dit qu'on propose une petite pause aux autres workies ? :coffee: \n Tu es sûrement pas seul.e à avoir la tête qui surchauffe :wink:" ,
                "fallback": "akoicaser1folebak",
                "callback_id": "kolbakeydi",
                "color": "#2cb42c",
                "attachment_type": "default",
                "actions":[
                    {
                        "name": "plan_coffee_break",
                        "text": "Oui, une pause !! :raised_hands:",
                        "type": "button",
                        "value": "yes"
                    },
                    {
                        "name": "plan_coffee_break",
                        "text": "Pas maintenant :x:",
                        "type": "button",
                        "value": "no"
                    }
                   
                ]
            }
        ]
    }

    return jsonify(interactive) #jsonify est une réponse (une classe slack)

@igetmad.route('/command/', methods=['POST'])
def jpp_start():
    print("OK")
    if request.method == 'POST' and request.form['command']=="/jpp":
        
        is_true = verify_slack_request(request)

        pprint.pprint(request.form)

        return coffee_break(request.form["user_id"])

@igetmad.route('/interactivity/', methods=['POST'])
def coffee_break_next():
    print(verify_slack_request(request))
    coffee_break_answer = json.loads(request.form['payload'])
    

    if coffee_break_answer['actions'][0]['value'] == 'no' and coffee_break_answer['actions'][0]["name"] =='plan_coffee_break':
        message = {
            "text": " Capito ! :ok_hand: Hésite pas à me recontacter via `/jpp`, je serai toujours là pour toi ! :right-facing_fist::fire::left-facing_fist: ",
            
        }

        no_answer = requests.post(coffee_break_answer['response_url'], json.dumps(message))
        print(no_answer.status_code,no_answer.text)
        return Response(status=200)

    if coffee_break_answer['actions'][0]['value'] == 'yes' and coffee_break_answer['actions'][0]["name"] =='plan_coffee_break':
        message = { "text" : " En route vers la pause café ! :rocket:"
            
        }

        yes_answer = requests.post(coffee_break_answer['response_url'], json.dumps(message))
        print(yes_answer.status_code,yes_answer.text)
    

        optin_menu = {
        "channel" : "général",
        "as_user" : "true",
        "text": "Salut à tous ! :spock-hand: \n "+mention_user(coffee_break_answer['user']['id'])+" propose une petite pause café :coffee:  *Qui en est* ?  \n C'est important d'aérer ses neurones et de se dégourdir les pattes ! :nerd_face:",
        "attachments": [
            {            
                "fallback": "akoicaser1folebak2",
                "callback_id": "kolbakeydi2",
                "color": "#2cb42c",
                "attachment_type": "default",
                "actions":[
                    {
                        "name": "coffee_response",
                        "text": "J'en suis!",
                        "type": "button",
                        "value": "coffee_yes"
                    }
                ]
            }]}

        coffee_optin = requests.post(
            slack_api_url+'chat.postMessage', 
            data=json.dumps(optin_menu),
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'Bearer '+os.getenv('SLACK_OAUTH_TOKEN')}
                )

        print(coffee_optin.status_code)
        print(coffee_optin.text)
        print("on est làààà")       

    


        return Response(status=200)
        

    if coffee_break_answer['actions'][0]['value'] == 'coffee_yes':
        channel1 = coffee_break_answer['channel']['name']
        username1 = coffee_break_answer['user']['id']
        print(channel1+username1)
        slack_api_call('chat.postEphemeral',os.getenv('SLACK_OAUTH_TOKEN'),channel=channel1,user=username1, text="Au top, profite de ton café et des autres workies ! :hugging_face:")
    
        punchline = ["est également chauuuuuuuuuuuuuuuuuud.e pour un café :fire:", "a besoin de sa dose :coffee:", "répond présent ! :raising_hand:", " débarque dans ta pause café :horse:", " fait la danse de la pause! :sunny:"]


        slack_api_call('chat.postMessage',os.getenv('SLACK_OAUTH_TOKEN'),channel=channel1,thread_ts=coffee_break_answer["message_ts"], text=mention_user(coffee_break_answer["user"]["id"])+punchline[random.randint(0,4)])

        
        return Response(status=200)
