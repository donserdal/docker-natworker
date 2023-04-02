from flask import Flask
from waitress import serve
from flask_restful import Resource, Api
from requests.auth import HTTPBasicAuth
from discord_webhook import DiscordWebhook, DiscordEmbed
#from paste.translogger import TransLogger
import logging, requests, json, urllib3, os
logger = logging.getLogger('waitress')
logger.setLevel(logging.INFO)

urllib3.disable_warnings()

app = Flask(__name__)
api = Api(app)

# Firewall Settings
endpoint     = os.environ.get('FW_ENDPOINT')   # 'https://<PFsense URL>/api/v1/firewall/nat/port_forward'
ApplyPoint   = os.environ.get('FW_APPLYPOINT') # 'https://<PFsense URL>/api/v1/firewall/apply'
username     = os.environ.get('FW_USERNAME')   # 'Username'
Password     = os.environ.get('FW_PASSWORD')   # 'Password'

# Webhook Settings
WebhookURL   = os.environ.get('WEBHOOK_URL')   # 'https://discord.com/api/webhooks/<ID>/<Auth_KEY>'
WebhookTitle = os.environ.get('WEBHOOK_TITLE') # 'Webhook Title'
WebhookColor = os.environ.get('WEBHOOK_COLOR') # 'Webhook Color'
WebhookUser  = os.environ.get('WEBHOOK_USER')  # 'Webhook User'

def GetNAT(port=None):
    # Auth Section
    JsonDict = {
        "local-port__contains": port
    }
    response = requests.get(endpoint, json=JsonDict, verify=False, auth = HTTPBasicAuth(username, Password))
    response_json = response.json()
    NATID = list(response_json['data'].keys())[0]
    if 'disabled' not in response_json['data']['{}'.format(NATID)]:
        RuleEnabled = True
    else:
        RuleEnabled = False
    return {'ID': NATID,"Status": RuleEnabled}

def DoNAT(id=None, Status=None):
    JsonDict = {
        "id": id,
        "disabled": Status
    }
    response = requests.put(endpoint, json=JsonDict, verify=False, auth = HTTPBasicAuth(username, Password))
    response_json = response.json()
    response = requests.post(ApplyPoint, verify=False, auth = HTTPBasicAuth(username, Password))
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

class DoNAT5081(Resource):
    def get(self):
        Result=DoNASFunc('5001')
        return Result

class DoNAT14659(Resource):
    def get(self):
        Result=DoNASFunc('14659')
        return Result

api.add_resource(DoNAT5081, '/fw-nat-nas')
api.add_resource(DoNAT14659, '/fw-nat-vpn')


if __name__ == '__main__':
    # Start server 
    serve(app, host="0.0.0.0", port=5000)
    
