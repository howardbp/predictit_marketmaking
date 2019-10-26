import csv
import requests
import time

EMAIL = 'xxxxxx'
PASS = 'xxxxxx'

def long_contracts():
        r = requests.get('https://www.predictit.org/api/Profile/Shares?sort=traded&sortParameter=ALL',headers=headers)
        data = r.json()
        markets = data['markets']

        lcs = list()
        for m in markets:
            contracts = m['marketContracts']
            yes = [k['contractId'] for k in contracts if k['userPrediction'] == 1 and k['userQuantity'] > 0]
            if len(yes) > 0:
                for i in yes:
                    lcs.append(i)
        return lcs


def login(uname,passowrd):
        data = {
                'email':uname,
                'password':passowrd,
                'grant_type':'password',
                'rememberMe':'true'
        }
        r = requests.post('https://www.predictit.org/api/Account/token',data=data)
        return r.json()

def make_headers():
        login_data = login(EMAIL,PASS)
        assert 'token_type' in login_data.keys(), 'issue logging in'
        headers = {
                'Authorization':'Bearer ' + login_data['access_token']
        }
        return headers

def cancel_bids_and_offers(contract_id):
        offers = {
                'offerType':'sell'
        }
        bids = {
                'offerType':'buy'
        }

        o = requests.post('https://www.predictit.org/api/Trade/CancelAllOffers/' + str(contract_id),headers=headers,data=offers)
        b = requests.post('https://www.predictit.org/api/Trade/CancelAllOffers/' + str(contract_id),headers=headers,data=bids)

def number_of_contracts(contract_id):

        r = requests.get('https://www.predictit.org/api/Profile/Shares?sort=traded&sortParameter=ALL',headers=headers)
        data = r.json()
        markets = data['markets']

        for market in markets:
        	contracts = market['marketContracts']
        	for contract in contracts:
        		if contract['contractId'] == contract_id:
        			return contract['userQuantity']
        			break
        return 0

def dealwzero(charin):
	try:
		return int(charin)
	except:
		return 0


def get_bbo(contract_id):
        r  = requests.get('https://www.predictit.org/api/Trade/{}/OrderBook'.format(str(contract_id)),headers=headers)
        data = r.json()
        if 'yesOrders' in data.keys():
                yes_orders = data['yesOrders']
        else:
                yes_orders = []

        if 'noOrders' in data.keys():
                no_orders = data['noOrders']
        else:
                no_orders = []

        if len(yes_orders) > 0:
                yes_orders.sort(key = lambda x : x['costPerShareYes'])
                best_offer = {'size':yes_orders[0]['quantity'],'offer':int(yes_orders[0]['costPerShareYes'] * 100)}
        else:
                best_offer = {'size':0,'offer':100}

        if len(no_orders) > 0:
                no_orders.sort(key = lambda x : x['costPerShareYes'],reverse=True)
                best_bid = {'size':no_orders[0]['quantity'],'bid':dealwzero(no_orders[0]['costPerShareYes']* 100)}
        else:
                best_bid = {'size':0,'bid':1}

        if len(yes_orders) > 1:
                next_best_offer =  {'size':yes_orders[1]['quantity'],'offer':int(yes_orders[1]['costPerShareYes'] * 100)}
        else:
                next_best_offer = {'size':0,'offer':99}

        if len(no_orders) > 1:
                next_best_bid =  {'size':no_orders[1]['quantity'],'bid':dealwzero(no_orders[1]['costPerShareYes']* 100)}
        else:
                next_best_bid = {'size':0,'bid':1}

        return best_bid,best_offer,next_best_bid,next_best_offer


def send_order(quantity,pricePerShare,contractId,side):
        #tradetype 1 is buy yes
        if side == 'buy':
                tradetype = '1'
                price = str(pricePerShare)
        else:
        		#trade type 3 is sell yes if you already own it (as opposed to buy no)
                tradetype = '3'
                price =  str(pricePerShare)

        data = {
                'quantity':str(quantity),
                'pricePerShare':price,
                'contractId':str(contractId),
                'tradetype':tradetype
        }

        r = requests.post('https://www.predictit.org/api/Trade/SubmitTrade',data=data,headers=headers)

        return r