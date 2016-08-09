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
bank = 10
run = 0

# aget API keys
# k.get_keys('C:\\test.txt')

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
    
    #conversion 1 
    if r1 in rates.keys():
        c1 = exch(capital,rates[r1])
    elif (r1[4:]+r1[:4]) in rates.keys():
        r1 = r1[4:]+r1[:4]
        c1 = exch(capital,(1/rates[r1]))
    else:
        r1=0
        c1 = exch(capital,r1)

    
    #second conversion
    if r2 in rates.keys():
        c2 = exch(c1,rates[r2])
    elif (r2[4:]+r2[:4]) in rates.keys():
        r2 = r2[4:]+r2[:4]        
        c2 = exch(c1,(1/rates[r2]))
    else:
        r2=0
        c2 = exch(c1,r2)

    
    #third conversion
    if r3 in rates.keys():
        capital = exch(c2,rates[r3])
    elif (r3[4:]+r3[:4]) in rates.keys():
        r3 = r3[4:]+r3[:4]        
        capital = exch(c2,(1/rates[r3]))
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
        rates[i] = float(ticker_info.json()['result'][i]['a'][0])
    
        
#run intialization and set up the universe of 3-way options
universe = initialize()

#execute
execute_algo2(run)

print("Finished!")