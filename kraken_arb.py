# -*- coding: utf-8 -*-
"""
Created on Sun Aug  7 22:02:13 2016

@author: galperins4
"""

# import modules and global variables
from Kraken import Kraken
from itertools import permutations
import time
# import datetime

# create object
k = Kraken()
rates={}
bank = 20
run = 0

# aget API keys
k.get_keys('C:\\test.txt')

# list of currencies and empty rates/trades table
currency = [i for i in k.get_asset_info().json()['result']]
asset_pairs = [i for i in k.get_tradable_asset_pairs().json()['result']]

#need to remove darkpools - manually update list or find a way to auto populate
darkpools = ['XXBTZEUR.d','XETHZJPY.d', 'XETHZCAD.d', 'XETHZEUR.d', 'XETHXXBT.d', 'XXBTZUSD.d', 'XXBTZGBP.d',
             'XETHZUSD.d', 'XXBTZCAD.d', 'XETHZGBP.d', 'XXBTZJPY.d']

for i in darkpools:
    asset_pairs.remove(i)

# testing execution
def execute_algo():
    run_sim()

# looping execution
def execute_algo2(t):
    #main loop
    while t<10:
        #run simulation and display results
        run_sim()
 
        #pause 15 seconds between API calls for loop
        time.sleep(10)        
        
        #increment counter
        t += 1
    
        '''# on last run, ask if user wants to continue executing loop
        if t == 100:
            repeat = input('Would you like to continue(Y or N)').lower()
            if repeat == 'y':
                # start while incrementent over and clear output
                t = 0
                clear_output()'''

                
def run_sim():
    #get rates
    get_rates()

    #run simulation and assign to result_set
    result_set = arb_sim()
    
    high = max(result_set, key=result_set.get)
    prof = max(result_set.values())
    perct = (prof / bank)*100

    print('\nThe 3-way arbitrage with highest opportunity is: ', high)
    print('Possible profit is:', (prof))
    print('% gain or loss is: ', (perct))    
    
    #trade functionality
    if perct>5:
        print('go for it')
    
    
    #example for opposite market - buy / quote price
    #trade1= k.add_standard_order('XXBTZUSD','buy','market','20.00', oflags='viqc')
    
    #example for market - sell / base price
    #trade2 = k.add_standard_order('XXBTZUSD','sell','market',balance)
    
    #balance = k.get_account_balance().json()['result']['XXBT']
    
    #get trade pairs to determine type of trade     
    t1_pair = ''.join(high[0:2])
    t2_pair = ''.join(high[1:])
    t3_pair = ''.join(high[-1::-2])
    tpairs = [t1_pair,t2_pair,t3_pair]
    print(tpairs)
    
    #if result is true - market is correct, if false - opposite market
    check = lambda x: x in rates.keys()    
    market_check = list(map(check,tpairs))
    print(market_check)
        
    #convert market_check to buy/sell
    convert = lambda x: 'sell' if x==True else 'buy'
    trade_convert = list(map(convert,market_check))
    print(trade_convert)
    
    #trade1
    if trade_convert[0]=='buy':
        reverse = tpairs[0][4:]+tpairs[0][:4]
        # k.add_standard_order(reverse,'buy','market','20.00', oflags='viqc')
    else:
        # k.add_standard_order(tpairs[0],'sell','market','20.00')
        pass
    
    #trade2 - get balance as input first
    #trade2_vol = k.get_account_balance().json()['result'][high[1]]
    if trade_convert[1]=='buy':
        reverse = tpairs[1][4:]+tpairs[1][:4]
        # k.add_standard_order(reverse,'buy','market',trade2_vol, oflags='viqc')
    else:
        # k.add_standard_order(tpairs[1],'sell','market',trade2_vol)
        pass    
    
    #trade3 - get balance as input first
    #trade3_vol = k.get_account_balance().json()['result'][high[2]]
    if trade_convert[2]=='buy':
        reverse = tpairs[2][4:]+tpairs[2][:4]
        # k.add_standard_order(reverse,'buy','market',trade3_vol, oflags='viqc')
    else:
        # k.add_standard_order(tpairs[2],'sell','market',trade3_vol)
        pass    
    
    '''#export for analysis
    if perct > 4.5:
        time = str(datetime.datetime.now())
        file = open('track.txt','a')
        file.write(str(high))
        file.write(',')
        file.write(str(perct))
        file.write(',')
        file.write(time)
        file.write('\n')
        file.close()    
        '''
    
    
def initialize():
    #unique combinations - groups of 3
    arb_universe = list(permutations(currency, 3))
        
    #initially just consider universe of combinations where it starts with USD
    population = list(filter(lambda x: x[:][0] =='ZUSD', arb_universe))
    
    return population
    
def arb_sim():
    #create empty profit dictionary
    pdict = {}
    
    #loop through 3-way combinations
    for i in universe:
        r1 = ''.join(i[0:2])
        r2 = ''.join(i[1:])
        r3 = ''.join(i[-1::-2])
    
        #check to see if pairs exists and if not revsere the rate    
            
        #output net profit/loss and record in dictionary and first/second trade leg values
        result = arb(bank,r1,r2,r3)
        pdict[i] = result
        
    return pdict
    
def arb(t1,r1,r2,r3):
    # define starting trade amount
    capital = t1
    #define lambda for exchange
    exch = lambda c, fx: c*fx
    
    #conversion checks
    # 1 - if in keys, use pair
    # 2 - if opposite in keys use 1/opposite
    # 3 - if neither of those passes it doesn't exist and set to 0    
    
    #if your market is equal - trade will be a sale (need bid) with base price
    #if your market is opposite - trade will be buy (need ask) with quote price    
    
    #conversion 1 
    if r1 in rates.keys():
        c1 = exch(capital,rates[r1][1])
    elif (r1[4:]+r1[:4]) in rates.keys():
        r1 = r1[4:]+r1[:4]
        c1 = exch(capital,(1/rates[r1][0]))
    else:
        r1=0
        c1 = exch(capital,r1)

    
    #second conversion
    if r2 in rates.keys():
        c2 = exch(c1,rates[r2][1])
    elif (r2[4:]+r2[:4]) in rates.keys():
        r2 = r2[4:]+r2[:4]        
        c2 = exch(c1,(1/rates[r2][0]))
    else:
        r2=0
        c2 = exch(c1,r2)

    
    #third conversion
    if r3 in rates.keys():
        capital = exch(c2,rates[r3][1])
    elif (r3[4:]+r3[:4]) in rates.keys():
        r3 = r3[4:]+r3[:4]        
        capital = exch(c2,(1/rates[r3][0]))
    else:
        r3=0        
        capital = exch(c2,r3)  
        
    return (capital - t1)

def get_rates():
    
    global rates
    #define permuations based on currencies identified for trading
    ticker_info = k.get_ticker_information(asset_pairs)
     
    #load asset pairs into rates with default value of None    
    rates = {i:None for i in asset_pairs}
        
    #use keys from rates to pull in last execute price from ticker info
    #format - ask, bid, last trade price
    for i in rates:
        rates[i] = [float(ticker_info.json()['result'][i]['a'][0]),
                  float(ticker_info.json()['result'][i]['b'][0])]
            
#run intialization and set up the universe of 3-way options
universe = initialize()

#execute multi-run
execute_algo2(run)

#execute single run
#execute_algo()

print("Finished!")
