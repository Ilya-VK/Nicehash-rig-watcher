from datetime import date, datetime
from time import mktime, sleep, strftime
import uuid
import hmac
import requests
import json
import re
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
    messages = []
    messages.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    try:
        account_data = api.get_accounts_for_currency('BTC')
    except:
        pass
    else:
        messages.append(f"Account balance: {float(account_data['totalBalance']) * 1000:>13.5f} mBTC")

    try:
        rigs_data = api.get_my_rigs()
    except:
        messages.append('Rigs data not available')
    else:
        messages.append(f"Unpaid amount on rigs: {float(rigs_data['unpaidAmount']) * 1000:.5f} mBTC")
        for rig in rigs_data['miningRigs']:
            messages.append('')
            for device in rig['devices']:
                row = []
                row.append(f"{rig['name']:<4}")
                if type(messages[-1]) is list:
                    if messages[-1][0] == row[-1]:
                        row[-1] = '    '
                device['name'] = device['name'].replace('Intel(R) Core(TM) ', '')
                device['name'] = device['name'].replace('GeForce ', '')
                device['name'] = device['name'].replace('Quadro ', '')
                device['name'] = re.sub(r"( CPU @ )\d[.]\d\d(GHz)", '', device['name'])
                row.append(f"{device['name']:<12}")
                row.append(f"{device['status']['enumName']:<8}")
                for speed in device['speeds']:
                    if device['status']['enumName'] != 'OFFLINE':
                        row.append(f"{speed['title']:<15} {float(speed['speed']):>5.2f}{speed['displaySuffix']}/s")
                        if device['revolutionsPerMinutePercentage'] > 0:
                            row.append(f"Fan: {device['revolutionsPerMinutePercentage']/100.0:>3.0%}")
                        if device['temperature'] > 0:
                            row.append(f"GPU:{device['temperature'] % 65536:>3.0f}°С")
                            row.append(f"HS/VRAM:{device['temperature'] / 65536:>3.0f}°С")
                messages.append(row)

    for item in messages:
        if type(item) is str:
            print(item)
        elif type(item) is list:
            print(*item, sep='   ')
    print()
    sleep(5)