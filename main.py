from multiprocessing import Process
import logging
import config
import sys

from marketDataWS import BinanceWsSpotMD,BinanceWsFuturosMD

logger = logging.getLogger("Binance-MAIN")
logger.setLevel(config.logLevel)

if __name__ == '__main__':
    if(len(sys.argv)<2):        
        ENV = "DESARROLLO"
    else:
        if sys.argv[1] in ( "DESARROLLO", "PRODUCCION"):
            ENV = sys.argv[1]
        else:
            ENV = "DESARROLLO"
        
    logger.info(f"ENV : {ENV}")
    env_variables = config.getEnv(ENV)

    s = Process(target=BinanceWsSpotMD, kwargs={**env_variables,'stream':"!bookTicker",'auto_start':True},
                        name='Spot'
                        )
    s.start()
    
    f = Process(target=BinanceWsFuturosMD, kwargs={**env_variables,'stream':"!bookTicker",'auto_start':True},
                        name='Fut'
                        )
    f.start()    
    
    #binFutUserData = BinanceWsFuturosUserData( **env_variables )
    
    while True:
        pass