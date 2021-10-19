import logging

from config import *
from models import *
from binanceBase import BinanceREST


logger = logging.getLogger("Binance-SPOT")
logger.setLevel(logLevel)

class BinanceSpotRest(BinanceREST):
    
    def get_exchange_info(self):
        r = self.__send_public_request__('/api/v3/exchangeInfo')
        print(r)
        
    def __get_trades__(self,**params):
        orders = []
        try:
            r = self.__send_signed_request__('GET','/api/v3/myTrades', payload=params)
            for t in r:
                print(t)
   
                report = Report(type=TYPE_INFO_TRADE, 
                        status=STATUS_COMPLETED,
                        exec_type=EXEC_TYPE_TRADE,
                        exchange=self.config.get("NAME_EXCHANGE"),
                        book=t.get('book'),
                        order_id=t.get('orderId'),
                        price=float(t.get('price')),
                        datetime=float(t.get('time')),
                        qty=abs(float(t.get('qty'))),
                        fees_qty=abs(float(t.get('commission'))),
                        fees_currency=t.get('commissionAsset'),
                        currency=t.get('minor_currency'),
                        crypto=t.get('major_currency'),
                        trade_id=int(t.get('id')),
                        side=(0 if t.get('isBuyer') else 1),
                        oid_maker=(t.get('orderId') if t.get('isMaker') else None),
                        oid_taker=(t.get('orderId') if not t.get('isMaker') else None),
                        )
                orders.append(report)
        except Exception as e:
            logger.error(e,exc_info=True)
        return orders 
        
    def __get_all_orders__(self,**params):
        orders = []
        try:
            r = self.__send_signed_request__('GET','/api/v3/allOrders', payload=params)
            for o in r:            
                if o.get('status') == "NEW":
                    st = STATUS_NEW
                elif o.get('status') == "PARTIALLY_FILLED":
                    st = STATUS_PARTIAL              
                elif o.get('status') == "FILLED":
                    st = STATUS_COMPLETED
                elif o.get('status') == "CANCELED":                
                    st = STATUS_CANCELLED
                elif o.get('status') == "EXPIRED":                
                    st = STATUS_EXPIRED
                    
                    
                report = Report(type= TYPE_REPORT,
                                book=o.get('symbol'),
                                exchange=self.config.get("NAME_EXCHANGE"),
                                order_type=o.get('type'),
                                crypto=o.get('symbol')[:3],
                                currency=o.get('symbol')[3:],
                                order_id=o.get('orderId'),
                                side=(0 if o.get('side')=='buy' else 1),
                                price=float(o.get('price')),
                                qty=float(o.get('origQty')),
                                leaves_qty=float(o.get('origQty'))-float(o.get('executedQty')),
                                cum_qty=float(o.get('executedQty')),
                                status=st,
                                client_id=o.get('clientOrderId'),
                                datetime=float(o.get('time'))
                )
                orders.append(report)
        except Exception as e:
            logger.error(e)
        return orders     



if __name__ == '__main__':
    # FUTUROS TESTNET
    #key 755ff87c3150a309547ed946f197e468e5243d80dab4cc5ade3b134b82744757
    #secret a9574bfab710c70ec03f30ff1d278c26391231c32e7b995a804234c7f77b0e60
    
    bf = BinanceSpotRest(base_url = 'https://binance.com', key='755ff87c3150a309547ed946f197e468e5243d80dab4cc5ade3b134b82744757',secret = 'a9574bfab710c70ec03f30ff1d278c26391231c32e7b995a804234c7f77b0e60')
    print(bf.__send_public_request__("/api/v3/ticker/bookTicker?symbol=BTCUSD"))