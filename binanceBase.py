import pika
import logging
import websocket
import config
import json
import hmac
import time
import hashlib
import requests
from urllib.parse import urlencode

logger = logging.getLogger("Binance-FUT")
logger.setLevel(config.logLevel)

class BinanceWS(object):
    def __init__(self, **kwargs):

        self.url = kwargs.get('url')
        self.stream = kwargs.get('stream')
   
        self.rabbit_url = kwargs.get('rabbit_url')
        self.rabbit_exchange = kwargs.get('rabbit_exchange')
        self.rabbit_routing_key  = kwargs.get('rabbit_routing_key')
        self.__connect_to_pika__()
        self.auto_start = kwargs.get('auto_start')
        self.__connect_to_binance__()

    def __connect_to_binance__(self):
        #start websocket connection        
        logger.warning(f"Iniciando websocket en : {self.url}")
        self.ws = websocket.WebSocketApp(self.url,
                                         on_open=self.on_open,
                                         on_message=self.on_message,
                                         on_error=self.on_error,
                                         on_close=self.on_close,
                                         )
        if self.auto_start:
            self.start()

    def __connect_to_pika__(self):
        try:
            logger.warning(f'Conectando RabbitMQ OUT {self.rabbit_url}')
            self.pika_connection = pika.BlockingConnection(pika.URLParameters(self.rabbit_url))
            self.pika_channel = self.pika_connection.channel()            
            logger.warning('RabbitMQ OUT OK')
            return True
        except Exception as e:
            logger.error(e, exc_info=True)
            return False
        
    def __send_pika__(self, msg_to_core):
        try:
            self.pika_channel.basic_publish(exchange=self.rabbit_exchange, routing_key=self.rabbit_routing_key, body=json.dumps(msg_to_core))
        except (pika.exceptions.ConnectionWrongStateError,
                pika.exceptions.StreamLostError,
                Exception) as e:
            logger.error(f'----------------------------------\n Pika Exception : {e}')
            logger.error(e,exc_info=True)
            logger.error("Pika Exception RECONECTANDO \n ----------------------------------")
            if  self.__connect_to_pika__():
                self.__send_pika__(msg_to_core)
            try:
                self.on_open(self.ws)
            except:
                self.__connect_to_binance__()
                
    def on_error(self, ws, error):
        logger.error(f'WebSocket Error {error} | Reconectando',exc_info=True)        
        #self.__connect_to_binance__()

    def on_close(self, ws,tres,cuatro):
        logger.error("WEB SOCKET CLOSED",exc_info=True)        
        #self.__connect_to_binance__()

    def on_open(self, ws):
        ws.send(json.dumps({'method': 'SUBSCRIBE','params': [f'{self.stream}'],'id':1}))
        logger.info(f'Subscribiendose al stream : {self.stream}')

    def start(self):
        self.ws.run_forever()        
        
class BinanceREST(object):
    def __init__(self,**kwargs):
        self.api_secret_rest = kwargs.get('api_secret_rest')
        self.api_key_rest = kwargs.get('api_key_rest')
        self.base_rest_url = kwargs.get('base_rest_url')
        
    def __hashing__(self,query_string):
        return hmac.new(self.api_secret_rest.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()

    def __get_timestamp__():
        return int(time.time() * 1000)

    def __dispatch_request__(self,http_method):
        session = requests.Session()
        session.headers.update({
            'Content-Type': 'application/json;charset=utf-8',
            'X-MBX-APIKEY': self.api_key_rest
        })
        return {
            'GET': session.get,
            'DELETE': session.delete,
            'PUT': session.put,
            'POST': session.post,
        }.get(http_method, 'GET')

    # used for sending request requires the signature
    def __send_signed_request__(self,http_method, url_path, payload={}):
        query_string = urlencode(payload, True)
        if query_string:
            query_string = "{}&timestamp={}".format(query_string, self.__get_timestamp__())
        else:
            query_string = 'timestamp={}'.format(self.__get_timestamp__())

        url = self.base_rest_url + url_path + '?' + query_string + '&signature=' + self.__hashing__(query_string)
        print("{} {}".format(http_method, url))
        params = {'url': url, 'params': {}}
        response =self.__dispatch_request__(http_method)(**params)
        return response.json()

    # used for sending public data request
    def __send_public_request__(self,url_path, payload={}):
        query_string = urlencode(payload, True)
        url = self.base_rest_url + url_path
        if query_string:
            url = url + '?' + query_string
        print("{}".format(url))
        response = self.__dispatch_request__('GET')(url=url)
        return response.json()

        