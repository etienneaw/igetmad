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



def create_new_event(user_id):
    interactive = {
        "text": "ok "+mention_user(user_id)+" tu es une baltringue qui arrive aps à se concentrer ?",
        "attachments": [
            {
                "text": "Commence par cdéfinir à quel point tu es un lâche",
                "fallback": "akoicaser1folebak",
                "callback_id": "kolbakeydi",
                "color": "#2cb42c",
                "attachment_type": "default",
                "actions":[
                    {
                        "name": "day",
                        "text": "lâche de compet'",
                        "type": "button",
                        "value": "tomorrow"
                    },
                    {
                        "name": "day",
                        "text": "lâche de Sevran",
                        "type": "button",
                        "value": "after tomorrow"
                    },
                    {
                        "name": "day",
                        "text": "lâche",
                        "type": "button",
                        "style": "danger",
                        "value": "later"
                    }
                ]
            }
        ]
    }

    return jsonify(interactive) #jsonify est une réponse (une classe slack)

@igetmad.route('/command/', methods=['POST'])
def start_command():
    if request.method == 'GET':
        return "get method"
    elif request.method == 'POST':
        is_true = verify_slack_request(request)

        pprint.pprint(request.form)

        return create_new_event(request.form["user_id"])