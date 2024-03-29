import logging

import config 
from models import *
from binanceBase import BinanceREST

logger = logging.getLogger("Binance-FUT")
logger.setLevel(config.logLevel)

class BinanceFuturosREST(BinanceREST):
    def __init__(self, **kwargs):
        logger.debug("Iniciando FUTUROS...")
        
        kwargs['api_secret_rest'] = kwargs.get('futuros_api_secret_rest')
        kwargs['api_key_rest'] = kwargs.get('futuros_api_key_rest')
        kwargs['base_rest_url'] = kwargs.get('futuros_base_rest_url')
        
        super(BinanceFuturosREST, self).__init__(**kwargs)
        '''
        self.getSymbols()
        for s in self.symbols:
            self.changeLeverage(s['symbol'])
            self.changeMargin(s['symbol'])
        ''' 
    
    def get_symbols(self):
        self.symbols = self.__send_public_request__('/dapi/v1/ticker/price')       
    
    def change_leverage(self,symbol,value=1):
        logger.debug(f"Cambiando leverage de {symbol} a {value}")
        r = self.__send_signed_request__('POST','/dapi/v1/leverage',payload={"symbol":symbol,"leverage":value})
    
    def change_margin(self,symbol,value="ISOLATED"):
        logger.debug(f"Cambiando margin de {symbol} a {value}")
        r = self.__send_signed_request__('POST','/dapi/v1/marginType',payload={"symbol":symbol,"marginType":value})
    
    def new_order(self,order):
        tif = order.get_value('time_in_force') 
        if tif not in ("GTC","IOC","FOK","GTX"):
           tif = None
        
        fFinal = {}
        fOrder = {
            "symbol":order.get_value('symbol').upper(),
            "side":("BUY" if order.get_value('side') == SIDE_COMPRA else "SELL"),                   
            "positionSide":None,
            "type":order.get_value('order_type').upper(),            
            "quantity":order.get_value('qty'),
            "reduceOnly":order.get_value('reduce_only'),
            "price":( order.get_value('price') if float(order.get_value('price')) != 0 else None),
            "newClientOrderId":order.get_value('client_id'),
            "stopPrice":( order.get_value('stop_price') if float(order.get_value('stop_price')) != 0 else None),
            "closePosition":order.get_value('close_position'),
            "activationPrice":order.get_value('activation_price'),
            "callbackRate":order.get_value('callback_rate'),
            "workingType":order.get_value('working_type'),
            "priceProtect":order.get_value('price_protect'),
            "timeInForce":tif,
            "newOrderRespType":"ACK"}
        
        for s in fOrder:            
            if fOrder[s] is not None:                
                fFinal[s] = fOrder[s]
                
        r = self.__send_signed_request__('POST','/dapi/v1/order',fFinal)

    def cancel_all_orders(self,**params):
        r = self.__send_signed_request__('DELETE','/dapi/v1/allOpenOrders',{"symbol":params.get('symbol')})
        print(r)
    
    def cancel_order(self,**params):
        orderToCancel = {}
        orderToCancel['symbol'] = params.get('symbol')
        if params.get('client_id'):
            orderToCancel['origClientOrderId'] = params.get('client_id')
        elif params.get('order_id'):
            orderToCancel['orderId'] = params.get('order_id')
        r = self.__send_signed_request__('DELETE','/dapi/v1/order',orderToCancel)
    
    def get_open_orders(self,**params):
        openOrders = []
        r = self.__send_signed_request__('GET','/dapi/v1/openOrders',{"symbol":params.get('symbol')})
        for o in r:
            order = Orden(
                    exchange=config.NAME,
                    type=TYPE_ORDER,
                    status=STATUS_NEW,
                    order_id=o.get('orderId'),
                    book=o.get('symbol'),
                    symbol=o.get('pair'),
                    client_id=o.get('clientOrderId'),
                    price=o.get('price'),
                    side = SIDE_VENTA if o.get('SELL') else SIDE_COMPRA,
                    order_type = o.get('type'),
                    time_in_force=o.get('timeInForce'),
                    qty=o.get('origQty'),
                    stop_price=o.get('stopPrice'),
                    datetime=o.get('time')
            )
            openOrders.append(order)
        print(openOrders)
            
    def get_trades(self,**params):
        trades = []
        r = bf.__send_signed_request__('GET','/dapi/v1/userTrades',{"symbol":params.get('symbol')})
        for t in r:
            report = Report(
                    exchange=config.NAME,
                    type=TYPE_TRADE,
                    status=STATUS_NEW,
                    book=t.get('symbol'),
                    trade_id=t.get('id'),
                    qty=t.get('qty'),
                    price=t.get('price'),
                    fees_qty=t.get('commission'),
                    fees_currency=t.get('commissionAsset'),
                    oid_maker= t.get('id') if t.get('maker') is True else None, 
                    oid_taker= None if t.get('maker') is True else t.get('id'),
                    side = SIDE_VENTA if t.get('SELL') else SIDE_COMPRA,
                    datetime = t.get('time'),
                    crypto=t.get('pair')[:3],
                    currency=t.get('pair')[3:],
                    order_id = t.get('orderId'),
            )
            trades.append(report)
        print(trades)
        
    def get_listen_key(self):
        return self.__send_signed_request__('POST','/dapi/v1/listenKey')
    
    def send_keep_alive_listen_key(self):
        self.__send_signed_request__('PUT','/dapi/v1/listenKey')
    
    def stop_listenKey(self):
        self.__send_signed_request__('DELETE','/dapi/v1/listenKey')
    
    def get_exchange_info(self):
        return self.__send_public_request__("/dapi/v1/exchangeInfo")

    def get_commision_rate(self,**params):
        return self.__send_signed_request__("GET","/dapi/v1/commissionRate",{"symbol":params.get('symbol')})
        

if __name__ == '__main__':
    # FUTUROS TESTNET
    #key 755ff87c3150a309547ed946f197e468e5243d80dab4cc5ade3b134b82744757
    #secret a9574bfab710c70ec03f30ff1d278c26391231c32e7b995a804234c7f77b0e60
    
    #SPOT TEST
    #KEY = '3VXKp7iG3eMiK89W7xU2U5zhZCW02LTtK4CVKxiI7By38CCu5fTvyLLWpKNbQZl8'
    #SECRET = 'L1w6RHF7FJZTL6H28esLfnr6XffLqRz4IJeAoPyse76tMEQeUyxcXqCwSlquUHw7'
    #BASE_URL = 'https://api.binance.com' # production base url
    #BASE_URL = 'https://testnet.binance.vision' # testnet base url
    
    bf = BinanceFuturosREST(base_rest_url = 'https://testnet.binancefuture.com', key='755ff87c3150a309547ed946f197e468e5243d80dab4cc5ade3b134b82744757',secret = 'a9574bfab710c70ec03f30ff1d278c26391231c32e7b995a804234c7f77b0e60')
    print(bf.__send_public_request__("/dapi/v1/exchangeInfo"))
    
    '''
    o  = Orden(
        {"exchange":"binance",
         "side":0,
         "symbol":"BTCUSD_PERP",
         "order_type":"market",
         #"time_in_force":"GTC",
         #"price":57040,
         "qty":"1000",
        })
    
    r = bf.cancelAllOrders(symbol='BTCUSD_211231')
    #r = bf.getOpenOrders(symbol='BTCUSD_211231')
    
    #r = bf.getTrades(symbol='BTCUSD_211231',order_id='517796')
    print(r)
    '''