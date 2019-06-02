import os
import json
from botocore.vendored import requests

api_key = os.environ['api_key']
api_url = "https://api.telegram.org/bot{}/".format(api_key)


def lambda_handler(event, context):
    data = json.loads(event['body'])
    chat_id = data['message']['chat']['id']
    echo_text = data['message']['text']
    url = "{}sendMessage?text={}&chat_id={}".format(api_url, echo_text,chat_id)
    requests.get(url)
    return {
            'statusCode': 200
            }
