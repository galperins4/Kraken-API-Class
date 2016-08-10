# -*- coding: utf-8 -*-
"""
Created on Sun Aug  7 21:59:18 2016

@author: galperins4
"""

import requests
import hashlib
import hmac
import base64
import urllib.parse
import time

class Kraken(object):
      
    def __init__(self,key = '',secret = ''):
        self.key = key
        self.secret = secret
        self.url = 'https://api.kraken.com'
        self.apiv = '0'
        self.pp = ('public','private')
        self.method = {'gst':'Time',
                       'gai':'Assets',
                       'gtap':'AssetPairs',
                       'gti':'Ticker',
                       'god':'OHLC',
                       'gob':'Depth',
                       'grt':'Trades',
                       'grsd':'Spread',
                       'gab':'Balance',
                       'gtb':'TradeBalance',
                       'goo':'OpenOrders',
                       'gco':'ClosedOrders',
                       'qoi':'QueryOrders',
                       'gth':'TradesHistory',
                       'gti2':'QueryTrades',
                       'gop':'OpenPositions',
                       'gli':'Ledgers',
                       'ql':'QueryLedgers',
                       'gtv':'TradeVolume',
                       'aso':'AddOrder',
                       'coo':'CancelOrder'}
        
    def get_keys(self,path):
        f = open(path,"r")
        self.key = f.readline().strip()
        self.secret = f.readline().strip()
    
    def _get_headers(self, path, req):

        '''
        HTTP Header
            API-Key = API key
            API-Sign = Message signature using HMAC-SHA512 of (URI path + SHA256(nonce + POST data)) and base64 decoded secret API key
        POST data:
            nonce = always increasing unsigned 64 bit integer
            otp = two-factor password (if two-factor enabled, otherwise not required)
        '''
    
        # encode postdata
        postdata = urllib.parse.urlencode(req)
        
        #encode nonce+POST data
        encoded = (str(req['nonce']) + postdata).encode()

        # message = URI path + SHA256(nonce + POST data)
        message = path.encode() + hashlib.sha256(encoded).digest()

        # get signature and signature digest
        signature = hmac.new(base64.b64decode(self.secret), message, hashlib.sha512)
        sigdigest = base64.b64encode(signature.digest())

        #define headers data
        headers = {'API-Key': self.key,'API-Sign': sigdigest.decode()}
        
        return headers
    
    #define public methods
    def get_server_time(self):
        return requests.get(self.url+'/'+self.apiv+'/'+self.pp[0]+'/'+self.method['gst'])
    
    
    def get_asset_info(self, info=None, aclass=None, asset=None):
        if asset == None:
            payload = {'info': info, 'aclass': aclass, 'asset': asset}
        else:
            payload = {'info': info, 'aclass': aclass, 'asset': ','.join(asset[:])}
        return requests.get(self.url+'/'+self.apiv+'/'+self.pp[0]+'/'+self.method['gai'], params=payload)
        

    def get_tradable_asset_pairs(self, info=None, pair=None):
        if pair == None:
            payload = {'info': info, 'pair': pair}
        else:
            payload = {'info': info, 'pair': ','.join(pair[:])}
        return requests.get(self.url+'/'+self.apiv+'/'+self.pp[0]+'/'+self.method['gtap'], params=payload)
    
    
    def get_ticker_information(self, pair):
        payload = {'pair': ','.join(pair[:])}
        return requests.get(self.url+'/'+self.apiv+'/'+self.pp[0]+'/'+self.method['gti'], params=payload)
    
    
    def get_OHLC_data(self, pair, interval=None, since=None):
        payload = {'pair': pair,'interval': interval, 'since': since}
        return requests.get(self.url+'/'+self.apiv+'/'+self.pp[0]+'/'+self.method['god'], params=payload)
    
    
    def get_order_book(self, pair, count=None):
        payload = {'pair': pair,'count':count}
        return requests.get(self.url+'/'+self.apiv+'/'+self.pp[0]+'/'+self.method['gob'], params=payload)
    
    
    def get_recent_trades(self, pair, since=None):
        payload = {'pair': pair, 'since': since}
        return requests.get(self.url+'/'+self.apiv+'/'+self.pp[0]+'/'+self.method['grt'], params=payload)
    
    
    def get_recent_spread_data(self, pair, since=None):
        payload = {'pair': pair, 'since': since}
        return requests.get(self.url+'/'+self.apiv+'/'+self.pp[0]+'/'+self.method['grsd'], params=payload)
    
    
    #define private methods

    def get_account_balance(self, req={}):
        
        urlpath = '/'+self.apiv+'/'+self.pp[1]+'/'+self.method['gab']
        req['nonce'] = int(1000*time.time())
        headers = self._get_headers(urlpath,req)
        
        return requests.post(self.url+'/'+self.apiv+'/'+self.pp[1]+'/'+self.method['gab'], data=req, headers=headers)
    
    def get_trade_balance(self, req={}, asset = 'ZUSD', **kwargs):
        
        #optional inputs - aclass
        urlpath = '/'+self.apiv+'/'+self.pp[1]+'/'+self.method['gtb']
        req = {'asset': asset, 'nonce': int(1000*time.time())}
        
        for k,v in kwargs.items():
            req[k]=v
        headers = self._get_headers(urlpath,req)    
       
        return requests.post(self.url+'/'+self.apiv+'/'+self.pp[1]+'/'+self.method['gtb'], data=req, headers=headers)
        
        
    def get_open_orders(self, req={}, **kwargs):
        
        #optional inputs - trades, userref
        urlpath = '/'+self.apiv+'/'+self.pp[1]+'/'+self.method['goo']
        req = {'nonce': int(1000*time.time())}
        
        for k,v in kwargs.items():
            req[k]=v
        headers = self._get_headers(urlpath,req)
        
        return requests.post(self.url+'/'+self.apiv+'/'+self.pp[1]+'/'+self.method['goo'], data=req, headers=headers)
        
    
    def get_closed_orders(self, req={}, ofs=0, **kwargs):
        
        #optional inputs - trades, userref, start, end, closetime
        urlpath = '/'+self.apiv+'/'+self.pp[1]+'/'+self.method['gco']
        req = {'ofs': ofs, 'nonce': int(1000*time.time())}
        
        for k,v in kwargs.items():
            req[k]=v
        headers = self._get_headers(urlpath,req)
                
        return requests.post(self.url+'/'+self.apiv+'/'+self.pp[1]+'/'+self.method['gco'], data=req, headers=headers)
    
    def query_orders_info(self, txid, req={}, **kwargs):
        
        #optional inputs - trades, userref
        #20 maximum for txid
        urlpath = '/'+self.apiv+'/'+self.pp[1]+'/'+self.method['qoi']
        req = {'txid': ','.join(txid[:]), 'nonce': int(1000*time.time())}
        
        for k,v in kwargs.items():
            req[k]=v
        headers = self._get_headers(urlpath,req)
                
        return requests.post(self.url+'/'+self.apiv+'/'+self.pp[1]+'/'+self.method['qoi'], data=req, headers=headers)
        
    def get_trades_history(self, req={}, ofs=0, **kwargs):
        
        #optional inputs - type, trades, start, end
        urlpath = '/'+self.apiv+'/'+self.pp[1]+'/'+self.method['gth']
        req = {'ofs': ofs, 'nonce': int(1000*time.time())}
        
        for k,v in kwargs.items():
            req[k]=v
        headers = self._get_headers(urlpath,req)
    
        return requests.post(self.url+'/'+self.apiv+'/'+self.pp[1]+'/'+self.method['gth'], data=req, headers=headers)
    
    def query_trades_info(self, txid, req={}, **kwargs):
        
        #optional inputs - trades
        urlpath = '/'+self.apiv+'/'+self.pp[1]+'/'+self.method['qti2']
        req = {'txid': ','.join(txid[:]), 'nonce': int(1000*time.time())}
         
        for k,v in kwargs.items():
            req[k]=v
        headers = self._get_headers(urlpath,req)
        
        return requests.post(self.url+'/'+self.apiv+'/'+self.pp[1]+'/'+self.method['qti2'], data=req, headers=headers)
    
    def get_open_positions(self, txid, req={}, **kwargs):
        
        #optional inputs - docalcs        
        urlpath = '/'+self.apiv+'/'+self.pp[1]+'/'+self.method['gop']
        req = {'txid': ','.join(txid[:]), 'nonce': int(1000*time.time())}
        
        for k,v in kwargs.items():
            req[k]=v
        headers = self._get_headers(urlpath,req)
                
        return requests.post(self.url+'/'+self.apiv+'/'+self.pp[1]+'/'+self.method['gop'], data=req, headers=headers)
    
    def get_ledgers_info(self, req={}, ofs=0, **kwargs):
        
        #optional inputs - aclass, asset(comma delimated), type, start, end
        urlpath = '/'+self.apiv+'/'+self.pp[1]+'/'+self.method['gli']
        req = {'ofs': ofs, 'nonce': int(1000*time.time())}
                
        for k,v in kwargs.items():
            req[k]=v
        headers = self._get_headers(urlpath,req)
                
        return requests.post(self.url+'/'+self.apiv+'/'+self.pp[1]+'/'+self.method['gli'], data=req, headers=headers)
    
    def query_ledgers(self, id, req={}):
        
        #NOTE: Can only query a max on 20
        urlpath = '/'+self.apiv+'/'+self.pp[1]+'/'+self.method['ql']
        req = {'id': ','.join(id[:]), 'nonce': int(1000*time.time())}
        headers = self._get_headers(urlpath,req)
        
        return requests.post(self.url+'/'+self.apiv+'/'+self.pp[1]+'/'+self.method['ql'], data=req, headers=headers)
    
    
    def get_trade_volume(self, req={}, **kwargs):
        
        #optional inputs = pair(comma delimited), fee-info
        urlpath = '/'+self.apiv+'/'+self.pp[1]+'/'+self.method['gtv']
        req = {'nonce': int(1000*time.time())}
        
        for k,v in kwargs.items():
            req[k]=v
        headers = self._get_headers(urlpath,req)
                
        return requests.post(self.url+'/'+self.apiv+'/'+self.pp[1]+'/'+self.method['gtv'], data=req, headers=headers)
    
    def add_standard_order(self, pair, otype, ordertype, volume, req={}, **kwargs):
        
        #Example usage add_standard_order('XETHZUSD','buy','market','0.10')
        #Currency pair trading - Pair X/Y = ETH / USD in this example
        #If Buy, Buy X/ETH, Sell Z/USD
        #If Sell, Sell X/ETH, Buy Z/USD 
        urlpath = '/'+self.apiv+'/'+self.pp[1]+'/'+self.method['aso']
        req = {
            'pair': pair,
            'type': otype,
            'ordertype': ordertype,
            'volume': volume,
            'nonce': int(1000*time.time())
            }
        
        for k,v in kwargs.items():
            req[k]=v
        headers = self._get_headers(urlpath,req)
                
        return requests.post(self.url+'/'+self.apiv+'/'+self.pp[1]+'/'+self.method['aso'], data=req, headers=headers)
    
    def cancel_open_order(self, txid, req={}):
        
        urlpath = '/'+self.apiv+'/'+self.pp[1]+'/'+self.method['coo']
        req = {'txid': txid, 'nonce': int(1000*time.time())}
        headers = self._get_headers(urlpath,req)
        
        return requests.post(self.url+'/'+self.apiv+'/'+self.pp[1]+'/'+self.method['coo'], data=req, headers=headers)
