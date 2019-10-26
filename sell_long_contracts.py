from post import *

def cancel_contract_sales(contract_id):
        data = {
                'offerType':'sell'
        }
        r = requests.post('https://www.predictit.org/api/Trade/CancelAllOffers/' + str(contract_id),headers=headers,data=data)
        return r


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
        yes_orders = data['yesOrders']
        no_orders = data['noOrders']
        #I think this is done already - but to be safe:
        yes_orders.sort(key = lambda x : x['costPerShareYes'])
        no_orders.sort(key = lambda x : x['costPerShareYes'],reverse=True)

        best_bid = {'size':no_orders[0]['quantity'],'bid':dealwzero(no_orders[0]['costPerShareYes']* 100)}
        best_offer = {'size':yes_orders[0]['quantity'],'offer':int(yes_orders[0]['costPerShareYes'] * 100)}
        return best_bid,best_offer

	#we have to look a the best bid fo no

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

headers = make_headers()

with open('sell_contracts.csv','rb') as inf:
	working_contracts = [int(k[0]) for k in list(csv.reader(inf)) if len(k) > 0 and all(not f.isalpha() for f in k[0])]
inf.close()

for cont in working_contracts:
	cancel_contract_sales(cont)

	bb,bo = get_bbo(cont)

	if bo['offer'] - 1 == bb['bid']:
		offer = max(2,bo['offer'])
	elif bo['size'] < 20:
		offer = max(2,bo['offer'])
	else:
		offer = max(2,bo['offer'] - 1)

	size = number_of_contracts(cont)

	if size > 0:
		send_order(size,offer,cont,'sell')

	time.sleep(2)