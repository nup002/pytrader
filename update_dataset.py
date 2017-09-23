from api.bitfinex import client
import configparser
from datasets import DatasetHandler
from colorama import init

#Read the config file
config = configparser.ConfigParser()
config.read('config.ini')
candlespath = config['DATASETS']['candles_dataset_path'] #Get candles dataset filepath

#Initiate colorama for colored terminal output text
init(autoreset=True)

#Get the bitfinex API client
apiClient = client.Public()

#Get the candles dataset handler
handler = DatasetHandler.DatasetHandler(candlespath)

#syncronize candles dataset with bitfinex
handler.syncDatafile(apiClient)