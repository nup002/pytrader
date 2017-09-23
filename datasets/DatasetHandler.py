import os
import h5py
import pprint
import progressbar
import time
import datetime
from colorama import Fore, Back, Style
#Handler class for the HDF5 datasets used in pytrader

class CandlesHandler:
    """A dataset handler class that handles the hdf5 files used for storing data in pytrader"""
    
    def __init__(self, dataset_folder):
        #Initiate variables
        #Load dataset settings
        #Check if the dataset exists
        dataset_name = "candles_dataset.hdf5"
        self.dataset_path = dataset_folder + "\\" + dataset_name
        
        filelist = os.listdir(dataset_folder)
        if dataset_name not in filelist:
            print("Could not find the dataset named \"{}\" in the folder \"{}\". Existing files in this path:".format(dataset_name, os.path.dirname(os.path.realpath(__file__))))
            for file in filelist:
                print("\t" + file)
            while True:
                answer = input("Do you wish to create the file \"{}\"? [y/n] ".format(dataset_name)).lower()
                if answer == 'y':
                    break
                elif answer == 'n':
                    print("Exiting pytrader.")
                    exit()
                else:
                    print("Not a valid answer.")
        
        
        self._openHDF5()
            
    
    def _openHDF5(self):
        self.candlesfile = h5py.File(self.dataset_path, "a")
        #Check if the dataset has an entry in the configurations file.
        # if file_name[:-5] not in self.config.sections():
            # print("""Could not find an entry for the file \"{}\" in the dataset configurations file \"datasetsconfig.ini\". 
            # You must add an entry with the following format:
                # [<filename (without .hdf5 ending)>]
                    # [GROUP:<filename>.<group>]
                        # [DATASET:<filename>.<group>.<dataset>]
                            # datatype = <f, i8, ui8, i16, ui16, i32, ui32, etc. Leave blank to default to float (f).>
                            # dimensions = <1 or 2 or 3...>
                            # dim0_size = <size of dimension 0>
                            # dim<n>_size = <size of dimension <n>>""".format(file_name))
            # exit()
            
        #We obtain the required structure of the datafile.
        
        #Check if the necessary datasets exists within the hdf5 file
        required_datasets = ['1m', '5m', '15m', '30m', '1h', '3h', '6h', '12h', '1D', '7D', '14D', '1M']
        a = self.candlesfile
        existing_objects = a.keys()
        
        for r in required_datasets:
            if r not in existing_objects:
                print("Could not find dataset \"{}\" in the hdf5 file \"{}\". Creating.".format(r, file_name))
                a.create_dataset(r, (0, 6), maxshape=(None,6))
                
                
    
    # def _parseconfig(self, config)
    # configdict = defaultdict(dict)
    
    # #Goes through the config object and adds elements to a nested  dictionary
    # current_branch = config.sections()[0]
    # configdict[current_branch] = {}
    
    # #Locate those elements that are children of the current element
    # #If the element starts with "DATASET" we stop.
    # children = []
    # for section in config.sections():
        # if not current_branch.startswith("DATASET"):
            # if re.search(current_branch + '\.[^\.]+', section)
                # children.append(section)
        # else:
            # leaves = config[current.branch]
            # a = leaves
    # for child in children:
        
        
        
    def syncDatafile(self, client):
        #updates the dataset so that it contains all candles for all time.
        #This takes a long time to run the first time.
        file = self.candlesfile
        for dataset_name in file.keys():
            print(Fore.CYAN + "Checking the following dataset: {}".format(dataset_name))
            dataset = file[dataset_name]
            
            #Grab the most recent candle timestamp 
            newestts = client.get_candlesticks(dataset_name, 'tBTCUSD', 'last')[0][0]
            #Check if it matches the most current timestamp of the corresponding dataset
            try:
                latest_time = int(dataset[-1][0]) #Get the latest timestamp
            except ValueError:
                #In case of indexerror, the dataset has no data. Likely because it has just been created.            
                latest_time = 0   
            
            if latest_time != 0:
                latest_time_readable = datetime.datetime.fromtimestamp(int(latest_time)).strftime('%Y-%m-%d %H:%M:%S')
            else:
                latest_time_readable = "Dataset is empty!"
            newestts_readable = datetime.datetime.fromtimestamp(int(newestts)).strftime('%Y-%m-%d %H:%M:%S')
            print("Latest dataset timestamp: {}\tLatest exchange timestamp: {}\t==>\t".format(latest_time_readable, newestts_readable), end='')
            
            #We add 2 minute to each side to allow for errors in going from float to int
            if latest_time - 60*2 < newestts < latest_time + 60*2:
                print(Fore.GREEN + "The dataset is up to date.\n".format(dataset_name))
            else:         
                print(Fore.YELLOW + "The dataset is not up to date.".format(dataset_name))            
                #We get the maximum amount of allowed candles (up to 1000) from bitfinex that are available 
                #since the last candle was added to the dataset.
                candles = client.get_candlesticks(dataset_name, 'tBTCUSD', 'hist', limit=1000, start=int(latest_time+1)*1000, sort=1) 
                
                print(Fore.GREEN + "SYNCHRONIZING WITH BITFINEX...", end='')
                if latest_time == 0:
                    print(Fore.GREEN + " (from the beginning of time)")
                else:
                    print('')
                    
                #We get the first candle timestamp of the first call so we know where we began
                if len(candles)==0:
                    # In this case the api return is buggy. Primarily happens for the >1M return.
                    candlesOldestTs = newestts
                else:
                    candlesOldestTs = candles[0][0] 
                tsdiff = newestts - candlesOldestTs
                #Divide tsdiff (ms) with a number to get it into the timescale of the current dataset.
                if dataset_name == '1m':
                   s = (60)
                if dataset_name == '5m':
                   s = (60*5)   
                if dataset_name == '15m':
                   s = (60*15)   
                if dataset_name == '30m':
                   s = (60*30)    
                if dataset_name == '1h':
                   s = (60*60)
                if dataset_name == '3h':
                   s = (60*60*3)   
                if dataset_name == '6h':
                   s = (60*60*6)   
                if dataset_name == '12h':
                   s = (60*60*12)    
                if dataset_name == '1D':
                   s = (60*60*24)
                if dataset_name == '7D':
                   s = (60*60*24*7)   
                if dataset_name == '14D':
                   s = (60*60*24*14)   
                if dataset_name == '1M':
                   s = (60*60*24*31)    
                   
                callsNeeded = int(tsdiff/(s*1000))+1 #multiply s with 1000 since we get 1000 candles at a time
                if callsNeeded > 0:
                    bar = progressbar.ProgressBar(max_value=callsNeeded)
                    bar.update(0)
                    time.sleep(0.05) #Hack to get it to work
                    bar.update(1)
                callno = 0   
                finalCall = False
                while True:
                    try:
                        latest_time = int(dataset[-1][0]) #Get the latest timestamp of the dataset
                    except ValueError:
                        #In case of indexerror, the dataset has no data. Likely because it has just been created.
                        latest_time = 0
                    
                    if callno > 0 and not finalCall:
                        #We get the maximum amount of allowed candles (up to 1000) from bitfinex that are available 
                        #since the last candle was added to the dataset.
                        candles = client.get_candlesticks(dataset_name, 'tBTCUSD', 'hist', limit=1000, start=int(latest_time+1)*1000, sort=1)
                    
                    if finalCall:
                        #Some candle api calls are buggy and will not return the very last candle. 
                        #We use this if-case to check if it was obtained.
                        candles = client.get_candlesticks(dataset_name, 'tBTCUSD', 'last')
                        if candles[0][0] != latest_time:
                            dataset.resize(dataset.len()+len(candles), 0) #Resize to fit more candles.
                            dataset[-len(candles):, :] = candles #Add candles to the end
                        break
                        
                    #print("Candles returned: {}".format(len(candles)))
                    if len(candles)<1000:
                        finalCall = True

                    callno += 1
                    if callno <= callsNeeded:
                        bar.update(callno)
                    if len(candles)!=0:
                        #print("Got {} candles from the period {}-{}".format(len(candles), candles[0][0], candles[-1][0]))
                        dataset.resize(dataset.len()+len(candles), 0) #Resize to fit more candles.
                        dataset[-len(candles):, :] = candles #Add candles to the end
                print(Fore.GREEN + "\nDone!\n")