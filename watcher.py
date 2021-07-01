from datetime import datetime
from time import mktime, sleep, strftime
import uuid
import hmac
import requests
import json
from hashlib import sha256
from configparser import ConfigParser

class private_api: #stripped from original Nicehash example to only needed parts

    def __init__(self, host, organisation_id, key, secret, verbose = False):
        self.key = key
        self.secret = secret
        self.organisation_id = organisation_id
        self.host = host
        self.verbose = verbose

    def get_epoch_ms_from_now(self):
        now = datetime.now()
        now_ec_since_epoch = mktime(now.timetuple()) + now.microsecond / 1000000.0
        return int(now_ec_since_epoch * 1000)

    def request(self, method, path, query, body):

        xtime = self.get_epoch_ms_from_now()
        xnonce = str(uuid.uuid4())

        message = bytearray(self.key, 'utf-8')
        message += bytearray('\x00', 'utf-8')
        message += bytearray(str(xtime), 'utf-8')
        message += bytearray('\x00', 'utf-8')
        message += bytearray(xnonce, 'utf-8')
        message += bytearray('\x00', 'utf-8')
        message += bytearray('\x00', 'utf-8')
        message += bytearray(self.organisation_id, 'utf-8')
        message += bytearray('\x00', 'utf-8')
        message += bytearray('\x00', 'utf-8')
        message += bytearray(method, 'utf-8')
        message += bytearray('\x00', 'utf-8')
        message += bytearray(path, 'utf-8')
        message += bytearray('\x00', 'utf-8')
        message += bytearray(query, 'utf-8')

        if body:
            body_json = json.dumps(body)
            message += bytearray('\x00', 'utf-8')
            message += bytearray(body_json, 'utf-8')

        digest = hmac.new(bytearray(self.secret, 'utf-8'), message, sha256).hexdigest()
        xauth = self.key + ":" + digest

        headers = {
            'X-Time': str(xtime),
            'X-Nonce': xnonce,
            'X-Auth': xauth,
            'Content-Type': 'application/json',
            'X-Organization-Id': self.organisation_id,
            'X-Request-Id': str(uuid.uuid4())
        }

        s = requests.Session()
        s.headers = headers

        url = self.host + path
        if query:
            url += '?' + query

        if self.verbose:
            print(method, url)

        if body:
            response = s.request(method, url, data=body_json)
        else:
            response = s.request(method, url)

        if response.status_code == 200:
            return response.json()
        elif response.content:
            raise Exception(str(response.status_code) + ": " + response.reason + ": " + str(response.content))
        else:
            raise Exception(str(response.status_code) + ": " + response.reason)

    def get_my_rigs(self): # added for rig functionality
        return self.request('GET','/main/api/v2/mining/rigs2/', '', None)

    def get_accounts_for_currency(self, currency: str):
        return self.request('GET', '/main/api/v2/accounting/account2/' + currency, '', None)

config = ConfigParser()
config.read('config.ini')

host = config.get('main', 'host')
organisation_id = config.get('main', 'organisation_id')
key = config.get('main', 'key')
secret = config.get('main', 'secret')

api = private_api(host, organisation_id, key, secret)

while True:
    now = datetime.now()
    message =  "\n\n" + now.strftime("%Y-%m-%d %H:%M:%S")
    try:
        account_data = api.get_accounts_for_currency('BTC')
    except:
        pass
    else:
        message += ' Balance: {balance:.5f} mBTC. '.format(balance = float(account_data['totalBalance']) * 1000)
    try:
        rigs_data = api.get_my_rigs()
    except:
        message += '\nRigs data not available.'
    else:
        message += "Unpaid amount on rigs: {amount:.5f} mBTC.".format(amount = float(rigs_data['unpaidAmount']) * 1000)
        message += "\n------------------------------------------------------------------------------------------------------------------"
        for rig in rigs_data['miningRigs']:
            message += ('\nRig: {rigname: <10}').format(rigname = rig['name'])
            for device in rig['devices']:
                device_name = device['name']
                device_type = device['deviceType']['enumName']
                device_status = device['status']['enumName']
                if device_type == 'CPU':
                    message += ' | CPU:'
                    if device_status == "DISABLED":
                        message += ' not mining'
                    elif device_status == 'OFFLINE':
                        message += ' offline   '
                    else:
                        message += ' mining    '
                else:
                    message += (' | {devicename: <21}').format(devicename = device_name)
                    if device_status == 'MINING':
                        # VRAM/HotSpot: temperature / 65536, GPU Temp: temperature % 65536 # Hello, Nicehash, why not just simply add field to API output?..
                        GPU_temp = device['temperature'] % 65536
                        VRAM_temp = device['temperature'] / 65536
                        fan_percent = device['revolutionsPerMinutePercentage'] / 100.0
                        hash_rate = float(device['speeds'][0]['speed'])
                        message += ' GPU:{gputemp: >4.0f}°С VRAM:{vramtemp: >4.0f}°С | Fan:{fanpercent: >5.0%} | Hashrate:{hashrate: >6.2f}MH/s'\
                            .format(gputemp = GPU_temp, vramtemp = VRAM_temp, fanpercent = fan_percent, hashrate = hash_rate)
                    elif device_status == 'OFFLINE':
                        message += ' offline'
                    else:
                        message += ' inactive'
        print(message, end='\r')
    sleep(5)