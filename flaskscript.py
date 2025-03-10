from flask import Flask
from waitress import serve
from flask_restful import Resource, Api
from requests.auth import HTTPBasicAuth
from discord_webhook import DiscordWebhook, DiscordEmbed
#from paste.translogger import TransLogger
import logging, requests, json, urllib3, os, sys
#sys.tracebacklimit = 0
logger = logging.getLogger('waitress')
logger.setLevel(logging.INFO)

urllib3.disable_warnings()

app = Flask(__name__)
api = Api(app)

# Firewall Settings
getendpoint     = os.environ.get('FW_GETENDPOINT')    # 'https://<PFsense URL>/api/v2/firewall/nat/port_forwards'
patchendpoint   = os.environ.get('FW_PATCHENDPOINT')  # 'https://<PFsense URL>/api/v2/firewall/nat/port_forward'
ApplyPoint      = os.environ.get('FW_APPLYPOINT')     # 'https://<PFsense URL>/api/v2/firewall/apply'
FWAPI           = os.environ.get('FW_APIKey')         # 'API Key'

# Webhook Settings
WebhookURL      = os.environ.get('WEBHOOK_URL')       # 'https://discord.com/api/webhooks/<ID>/<Auth_KEY>'
WebhookTitle    = os.environ.get('WEBHOOK_TITLE')     # 'Webhook Title'
WebhookColor    = os.environ.get('WEBHOOK_COLOR')     # 'Webhook Color'
WebhookUser     = os.environ.get('WEBHOOK_USER')      # 'Webhook User'

headers = {
    "X-API-Key" : "{}".format(FWAPI),
    'accept' : 'application/json'
}


def GetNAT(port=None):
    # Auth Section
    JsonDict = {
        "local_port__contains": port
    }
    response = requests.get(getendpoint, headers=headers, json=JsonDict, verify=False)
    response_json = response.json()
    if response_json['code'] == 403:
        raise Exception("403 please check config") 
    
    if response_json['code'] == 401:
        raise Exception("401 Authentication failed")
    
    NATID = response_json['data'][0]['id']

    if response_json['data'][0]['disabled']:
        RuleEnabled = False
    else:
        RuleEnabled = True

    return {'ID': NATID,"Status": RuleEnabled}

def DoNAT(id=None, Status=None):
    JsonDict = {
        "id": id,
        "disabled": Status
    }
    response = requests.patch(patchendpoint, headers=headers, json=JsonDict, verify=False)
    response_json = response.json()
    response = requests.post(ApplyPoint, headers=headers ,verify=False)
    print("   - [DoNAT] Pushed status: {}".format(response.status_code))

def DoNASFunc(port=None):
    natstatus = GetNAT(port=port)
    print("[NAS] Current status is {} and port is {}".format(natstatus["Status"],port))
    if natstatus["Status"] == True:
        DoNAT(id=natstatus['ID'], Status=True)
        print("   Port {} Disabled".format(port))
        Status = "Disabled"
    else:
        DoNAT(id=natstatus['ID'], Status=False)
        print("   Port {} Enabled".format(port))
        Status = "Enabled"
    # Webhook:
    Description = "Port: {} is {}".format(port, Status)
    webhook = DiscordWebhook(url=WebhookURL, username=WebhookUser)
    # create embed object for webhook
    # you can set the color as a decimal (color=242424) or hex (color='03b2f8') number
    embed = DiscordEmbed(title=WebhookTitle, description=Description, color=WebhookColor)
    # add embed object to webhook
    webhook.add_embed(embed)
    response = webhook.execute()
    return {'NAT': Status, 'Port': port}

class DoNATNAS(Resource):
    def get(self):
        Result=DoNASFunc('5001')
        return Result

class DoNATVPN(Resource):
    def get(self):
        Result=DoNASFunc('51820')
        return Result

api.add_resource(DoNATNAS, '/fw-nat-nas')
api.add_resource(DoNATVPN, '/fw-nat-vpn')


if __name__ == '__main__':
    # Start server
    serve(app, host="0.0.0.0", port=5000)

