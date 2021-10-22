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
FUTUROS_REST_URL_TESTNET = 'https://testnet.binancefuture.com'
FUTUROS_API_KEY_REST_TESTNET ='755ff87c3150a309547ed946f197e468e5243d80dab4cc5ade3b134b82744757'
FUTUROS_API_SECRET_REST_TESTNET = 'a9574bfab710c70ec03f30ff1d278c26391231c32e7b995a804234c7f77b0e60'

SPOT_API_KEY_REST_TESTNET = "CGz2CC3WXWEYsAvRR5UJTsxvqZRXCR3HCAKtzr8QGXEqBhSmTP6OBfeDWjilHyUf"
SPOT_API_SECRET_TESTNET = "gHcQLqySIwJDXoVm2BU0qknjNS3EqFwms8IHR6UZqvk0C27bYRwtvoXDYv2bOxGn"
SPOT_REST_URL_TESTNET = 'https://testnet.binance.vision'

# WEB SOCKET
FUTUROS_WS_MD_USD_M_TESTNET = "wss://fstream.binancefuture.com/ws"
FUTUROS_WS_MD_COIN_M_TESTNET = "wss://dstream.binancefuture.com/ws"

# PRODUCCION ENDPOINTS
FUTUROS_WS_FUTUROS_MD_USD_M_PRODUCCION = "wss://fstream.binance.com/ws" #USD-M
FUTUROS_WS_FUTUROS_MD_COIN_M_PRODUCCION = "wss://dstream.binance.com/ws" #COIN-M
FUTUROS_WS_SPOT_MD_PRODUCCION = "wss://stream.binance.com:9443/ws"                         

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
        env_vars['ws_futuros_md'] = FUTUROS_WS_FUTUROS_MD_COIN_M_PRODUCCION
        env_vars['ws_spot_md'] = FUTUROS_WS_SPOT_MD_PRODUCCION
        env_vars['futuros_base_rest_url'] = FUTUROS_REST_URL_TESTNET
        env_vars['futuros_api_key_rest'] = FUTUROS_API_KEY_REST_TESTNET
        env_vars['futuros_api_secret_rest'] = FUTUROS_API_SECRET_REST_TESTNET
        env_vars['spot_base_rest_url'] = SPOT_REST_URL_TESTNET
        env_vars['spot_api_key_rest'] = SPOT_API_KEY_REST_TESTNET
        env_vars['spot_api_secret_rest'] = SPOT_API_SECRET_TESTNET
        env_vars['rabbit_url'] = PIKA_URL
        env_vars['rabbit_exchange'] = PIKA_EXCHANGE
        env_vars['rabbit_routing_key'] = PIKA_ROUTING_KEY_OUT
    
    return env_vars