import threading
import logging
import config
import json
import time 

from binanceBase import BinanceWS
from futurosRest import BinanceFuturosREST
from spotRest import BinanceSpotRest

logger = logging.getLogger("Binance-WS")
logger.setLevel(config.logLevel)

class BinanceWsSpotMD(BinanceWS):
    
    def __init__(self, **kwargs):        
        
        logger.warning("Iniciando SPOT MD")
        self.libros = []
        self.lastUID = 0
        self.data = {}
        self.spotRest = BinanceSpotRest(**kwargs)
        self.__get_fees__()
        kwargs['url'] = kwargs.get('ws_spot_md')
        super(BinanceWsSpotMD, self).__init__(**kwargs)
        
    def __get_fees__(self):
        r = self.spotRest.get_account_info()
        self.account_fees = {'makerCommission': r.get('makerCommission'), 'takerCommission': r.get('takerCommission'), 'buyerCommission': r.get('buyerCommission'), 'sellerCommission': r.get('sellerCommission')}           

    def on_message(self, ws, msg):
        '''
        {"u":235763753287,"e":"bookTicker","s":"BTCUSD_211231","ps":"BTCUSD","b":"57031.4","B":"688","a":"57031.5","A":"1316","T":1634072047318,"E":1634072047321}
        {
            "e":"bookTicker",         // Event type
            "u":17242169,             // Order book update Id
            "s":"BTCUSD_200626",      // Symbol
            "ps":"BTCUSD",            // Pair
            "b":"9548.1",             // Best bid price
            "B":"52",                 // Best bid qty
            "a":"9548.5",             // Best ask price
            "A":"11",                 // Best ask qty
            "T":1591268628155,        // Transaction time
            "E":1591268628166         // Event time
            }
        '''        
        try:            
            msg_to_core = None
            msg_json = json.loads(msg)
            
            if msg_json.get('s') is None: 
                logger.warning(f"SPOT : {msg_json}")
                return
            
            try:
                self.libros.index(msg_json.get('s'))
            except:
                self.libros.append(msg_json.get('s'))                
            
            if msg_json.get('s') not in self.data:
                self.data.update({msg_json.get('s'): {'lastUpdate':msg_json.get('u'),'Symbol': msg_json.get('s'),'Bid': msg_json.get('b'),'Ask': msg_json.get('a')} })
            
            if self.data[msg_json.get('s')]['lastUpdate'] > msg_json.get('u'):
                logger.error("Last Update del libro fallido")
                return
                           
            if self.data[msg_json.get('s')].get('Bid') != msg_json.get('b') or self.data[msg_json.get('s')].get('Ask') != msg_json.get('a'):                    
                
                self.data[msg_json.get('s')]['Bid'] = msg_json.get('b')
                self.data[msg_json.get('s')]['Ask'] = msg_json.get('a')
                
                msg_to_core = {"Header": {"MsgType": "MARKET_DATA"},
                                    "Body": {'Exchange': config.NAME,
                                            'Type':'SPOT',
                                            'Book': msg_json.get('s'),
                                            'Symbol': msg_json.get('s'),
                                            'Bid': msg_json.get('b'),
                                            'CantBid': msg_json.get('B'),
                                            'Ask': msg_json.get('a'),
                                            'CantAsk': msg_json.get('A'),
                                            **self.account_fees                                          
                                            }
                                    }

            if msg_to_core is not None:
                logger.warning(" "*50+f"SPOT {msg_to_core['Body']['Symbol']}")      
                self.__send_pika__(msg_to_core)
                    
        except Exception as e:
            logger.error(e,exc_info=True)
            logger.error(msg)
            logger.error(self.data[msg_json.get('s')])

class BinanceWsFuturosMD(BinanceWS):
    
    def __init__(self, **kwargs):        
        logger.warning("Iniciando FUTUROS MD")
        self.lastUID = 0
        self.data = {}
        self.futuros_fees = {}
        self.restFuturos = BinanceFuturosREST(**kwargs)
        self.__get_futuros_fee__()
        kwargs['url'] = kwargs.get('ws_futuros_md')
        super(BinanceWsFuturosMD, self).__init__(**kwargs)
    
    def __get_futuros_fee__(self):        
        symbols = self.restFuturos.get_exchange_info()
        for s in symbols['symbols']:
            self.futuros_fees[s['symbol']] = s['liquidationFee']
            
    def on_message(self, ws, msg):
        '''
        {"u":235763753287,"e":"bookTicker","s":"BTCUSD_211231","ps":"BTCUSD","b":"57031.4","B":"688","a":"57031.5","A":"1316","T":1634072047318,"E":1634072047321}
        {
            "e":"bookTicker",         // Event type
            "u":17242169,             // Order book update Id
            "s":"BTCUSD_200626",      // Symbol
            "ps":"BTCUSD",            // Pair
            "b":"9548.1",             // Best bid price
            "B":"52",                 // Best bid qty
            "a":"9548.5",             // Best ask price
            "A":"11",                 // Best ask qty
            "T":1591268628155,        // Transaction time
            "E":1591268628166         // Event time
            }
        '''        
        try:
            msg_to_core = None
            msg_json = json.loads(msg)
            
            if msg_json.get('e') == 'bookTicker':                
                
                if msg_json.get('s').find("PERP") >0 :
                    #Descarto los perpetuos
                    return

                if msg_json.get('ps') not in self.data:
                    r = self.restFuturos.get_commision_rate(symbol=msg_json.get('s'))                    
                    self.data.update({msg_json.get('ps'): {'lastUpdate':msg_json.get('u'),'Symbol': msg_json.get('s'),'Bid': msg_json.get('b'),'Ask': msg_json.get('a'), 'makerCommissionRate':r.get('makerCommissionRate'),'takerCommissionRate':r.get('takerCommissionRate') } })
                    logger.warning(f"FUTUROS : {self.data.keys()}")
            
                if self.data[msg_json.get('ps')]['lastUpdate'] > msg_json.get('u'):
                    logger.error("Last Update del libro fallido")
                    return
                
                if self.data[msg_json.get('ps')].get('Bid') != msg_json.get('b') or self.data[msg_json.get('ps')].get('Ask') != msg_json.get('a'):                    
                    
                    self.data[msg_json.get('ps')]['Bid'] = msg_json.get('b')
                    self.data[msg_json.get('ps')]['Ask'] = msg_json.get('a')
                    
                    msg_to_core = {"Header": {"MsgType": "MARKET_DATA"},
                                        "Body": {'Exchange': config.NAME,
                                                'Type':'FUT',
                                                'Book': msg_json.get('ps'),
                                                'Symbol': msg_json.get('s'),
                                                'Bid': msg_json.get('b'),
                                                'CantBid': msg_json.get('B'),
                                                'Ask': msg_json.get('a'),
                                                'CantAsk': msg_json.get('A'),
                                                'LiquidationFee':self.futuros_fees[msg_json.get('s')],
                                                'makerCommissionRate':self.data.get(msg_json.get('ps')).get('makerCommissionRate'),
                                                'takerCommissionRate':self.data.get(msg_json.get('ps')).get('takerCommissionRate')
                                                }
                                        }  
               
                if msg_to_core is not None:
                    logger.warning(f"FUT {msg_to_core['Body']['Symbol']}")
                    self.__send_pika__(msg_to_core)
            else : 
                logger.warning(f"FUT : {msg_json}")
                       
        except Exception as e:
            logger.error(e)

class BinanceWsFuturosUserData(BinanceWS):
    
    def __init__(self, **kwargs):
        self.br = BinanceFuturosREST(base_url = kwargs.get('base_rest_url'), 
                                key = kwargs.get('api_key_rest'),
                                secret = kwargs.get('api_secret_rest'))
        self.listenKey = self.br.getListenKey()
        logger.debug(self.listenKey)
        kwargs['url'] = kwargs.get('ws_futuros_md')+"/"+self.listenKey.get('listenKey')
        super(BinanceWsFuturosUserData, self).__init__(**kwargs)
        threading.Thread(name=f"KeepAliveKey",
                                 target=self.keepAlive() ).start()        

    def keepAlive(self):
        while True:            
            time.sleep(3500)
            self.br.sendKeepAliveListenKey()
            logger.info(f'Sending Keep Alive ListenKey')

    def on_open(self, ws):
        #ws.send(json.dumps({"method": "REQUEST","params":[self.listenKey.get('listenKey')+"@position",self.listenKey.get('listenKey')+"@balance"],"id": 121 }))
        logger.info(f'Subscribiendose al  listenKey')

    def on_message(self, ws, msg):  
        try:
            msg_json = json.loads(msg)
            if msg_json.get('e') == "ORDER_TRADE_UPDATE":                
                order = msg_json['o']                
                logger.debug(f"Execution report  : {order['x']} Status : {order['X']} filled : {order['l']} id : {order['i']} price : {order['L']} average price : {order['ap']}")
            #self.__send_pika__(msg_to_core)
        except Exception as e:
            logger.error(e)
    
    