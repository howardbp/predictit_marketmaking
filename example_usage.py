from post import *

headers = make_headers()

with open('/home/pi/predictit/marketmaking/making_markets.csv','rb') as inf:
	make_markets = [int(k[0]) for k in list(csv.reader(inf)) if len(k) > 0 and all(not f.isalpha() for f in k[0])]
inf.close()


join_market_size = 30
# first, cancel all current sales in the working contracts
for cont in make_markets:
	cancel_bids_and_offers(cont)

	bb,bo,nbb,nbo = get_bbo(cont)
#	print bb, bo, cont

	long_contracts = number_of_contracts(cont)

	if long_contracts == 0:
		size = 50
		if bb['size'] < 5:
			price = max(nbb['bid'],1)
		elif (bb['bid'] + 1 == bo['offer']) or (bb['size'] <= join_market_size):
			price = min(98,bb['bid'])
		else:
			#otherwise increment the bid by one cent
			price = min(98,bb['bid'] + 1)
		side = 'buy'


	else:
		size = long_contracts
		if bo['size'] < 5:
			price = min(99,nbo['offer'])
		elif (bo['offer'] - 1 == bb['bid']) or (bo['size'] <= join_market_size):
			price = max(2,bo['offer'])
		else:
			price = max(2,bo['offer'] - 1)

		side = 'sell'

	send_order(size,price,cont,side)
	time.sleep(2)
