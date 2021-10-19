import sys
import logging
import coloredlogs

logLevel = logging.WARNING
NAME = "binanace"

LOG_FORMATTER_SRT = f'[%(levelname)-5s | %(asctime)-15s | %(name)-15s | %(funcName)-10s ]\n%(message)s\n'+'-'*100
logging.basicConfig(format=LOG_FORMATTER_SRT)
if sys.platform != 'win32':
	coloredlogs.install( level=logLevel, fmt=LOG_FORMATTER_SRT)

# TESTNET BASE REST ENDPOINT
BASE_REST_URL_TESTNET = 'https://testnet.binancefuture.com'
API_KEY_TESTNET ='755ff87c3150a309547ed946f197e468e5243d80dab4cc5ade3b134b82744757'
API_SECRET_TESTNET = 'a9574bfab710c70ec03f30ff1d278c26391231c32e7b995a804234c7f77b0e60'
# TESTNET WEBSOCKET FUTUROS
WS_FUTUROS_MD_TESTNET_USD_M = "wss://fstream.binancefuture.com/ws"
WS_FUTUROS_MD_TESTNET_COIN_M = "wss://dstream.binancefuture.com/ws"

# PRODUCCION ENDPOINTS
WS_FUTUROS_MD_PRODUCCION_USD_M = "wss://fstream.binance.com/ws" #USD-M
WS_FUTUROS_MD_PRODUCCION_COIN_M = "wss://dstream.binance.com/ws" #COIN-M
WS_SPOT_MD_PRODUCCION = "wss://stream.binance.com:9443/ws"                         

#RABBIT CONFIGS
PIKA_USER = 'algo203'
PIKA_PASSWORD = 'guest'
PIKA_PORT = 5672
PIKA_HOST = "192.168.1.186"
PIKA_EXCHANGE = "exchange_gui_crypto_futuros"
PIKA_ROUTING_KEY_OUT = 'WEB.CRYPTO_FUTUROS_CORE.Crypto_Futuros.MD'
PIKA_URL = f'amqp://{PIKA_USER}:{PIKA_PASSWORD}@{PIKA_HOST}:{PIKA_PORT}/%2F?connection_attempts=3&heartbeat=30'


def getEnv(env):
    env_vars = {}
    if env=="DESARROLLO":
        env_vars['ws_futuros_md'] = WS_FUTUROS_MD_PRODUCCION_COIN_M
        env_vars['ws_spot_md'] = WS_SPOT_MD_PRODUCCION
        env_vars['base_rest_url'] = BASE_REST_URL_TESTNET
        env_vars['api_key_rest'] = API_KEY_TESTNET
        env_vars['api_secret_rest'] = API_SECRET_TESTNET
        env_vars['rabbit_url'] = PIKA_URL
        env_vars['rabbit_exchange'] = PIKA_EXCHANGE
        env_vars['rabbit_routing_key'] = PIKA_ROUTING_KEY_OUT
    
    return env_vars