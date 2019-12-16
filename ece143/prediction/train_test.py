import csv
import os
import sys
from collections import defaultdict

import numpy as np
import pandas as pd

import tensorflow as tf
from tensorflow.keras import layers
from keras.models import load_model

class PredictModel(object):
    '''The class of machine learning model. It was implemented for initializing
    the model, tuning model parameters, and predict the delay/cancel.
    '''
    def __init__(self, input_size, lr=0.01, model_path=None):
        '''Initialize the deep learning model.
        @param input_size: the length of input feature array
        @type input_size: int
        @param lr: learning rate of ML model
        @type lr: float
        @param model_path: the dir path where stored the pretrain model
        @type model_path: str 
        @return: None
        '''
        
        assert isinstance(input_size, int)
        assert input_size>0
        assert isinstance(lr, float)
        assert 0<lr<1

        self.input_size = input_size
        self.lr = lr
        if not model_path:
            self.model_path = './model'
            self.model = self.InitialModel()
            if not os.path.exists(self.model_path):
                os.mkdir(self.model_path)
        else:
            assert isinstance(model_path, str)
            self.model = load_model(model_path)
        
    def InitialModel(self):
        '''Model initialization. Make a 3 full-connected layers then sequencing them.
        @return: None
        '''
        model = tf.keras.Sequential([
            layers.Dense(256, activation='relu', input_shape=(self.input_size,)),
            layers.Dense(1024, activation='relu'),
            layers.Dense(512, activation='relu'),
            layers.Dense(2, activation='softmax')
        ])
        model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])
        return model
    
    def TrainModel(self, train_set, train_label, model_id, sub_epochs=10):
        '''Tuning model parameters. It splits the input data to 80% as training set 
        and 20% as validation set. Then fit the prediction to 2 classes: True or False,
        corresponding to whether the flight will delay/cancel. In each epochs, the model
        is saved in model dir.
        @param train_set: set of training data, observation features.
        @type train_set: np.ndarray 
        @param train_label: set of target labels. 
        @type train_label: np.ndarray
        @param model_id: the model id/trained epoches
        @type model_id: int
        @param sub_epochs: number of training loops for each training set.
        @type sub_epochs: int
        @return: None
        '''
        
        assert isinstance(train_set, np.ndarray)
        assert isinstance(train_label, np.ndarray)
        assert isinstance(model_id, int)
        assert model_id>=0
        assert isinstance(sub_epochs, int)
        assert sub_epochs>0
        
        self.model.fit(train_set, train_label, epochs=sub_epochs,validation_split=0.2)
        model_name = self.model_path+'/model_'+str(model_id)
        self.model.save(model_name)
    
    def Predict(self, input_data):
        '''Predict whether the flight will delay/cancel.
        @param input_data: array of features.
        @type input_data: np.ndarray
        @return: prediction array
        @rtype: np.ndarray.
        '''
        assert isinstance(input_data, np.ndarray)
        return self.model.predict(input_data)

def EncodeAirline(airline):
    '''Change the classes to one-hot code.
    @param airline: airline code.
    @type airline: str
    @return: array of one-hot key
    @rtype: list
    '''
    
    assert isinstance(airline, str)
    airline_set = {'F9':0, 'B6':1, 'EV':2, 'OO':3, 'UA':4, 'AA':5, 'WN':6, 'DL':7, 'HA':8, 'AS':9}
    assert airline in airline_set
    airline_hotkey = [0]*len(airline_set)
    if airline in airline_set:
        airline_hotkey[airline_set[airline]] += 1
    return airline_hotkey
    
    
def EncodeDelayData(df_airline, airport_info):
    ''''Change the dataframe to array of training set. The format of input feature is 
    [encoded_airline, lat, longtitude, elevation_ft, month-day].
    
    @param df_airline: data frame of 
    @type airline: pd.DataFrame
    @param df_airline: airport information 
    @type airline: dict
    @return: train set and label
    @rtype: tuple of list
    '''
    assert isinstance(df_airline, pd.DataFrame)
    assert isinstance(airport, dict)
    
    train_set = []
    test_set = []
    label_train = []
    label_test = []
    N_data = len(df_airline)
    delay_types=['WEATHER_DELAY','CARRIER_DELAY','NAS_DELAY','SECURITY_DELAY','LATE_AIRCRAFT_DELAY']
    airline_set = {'F9':0, 'B6':1, 'EV':2, 'OO':3, 'UA':4, 'AA':5, 'WN':6, 'DL':7, 'HA':8, 'AS':9}
    for k in range(N_data):
        carrier = df_airline['OP_CARRIER'][k]
        if carrier not in airline_set: continue
        date = df_airline['FL_DATE'][k].split('-')
        month = [int(date[1]+date[2])]
        airport_out = df_airline['ORIGIN'][k]
        airport_in = df_airline['DEST'][k]
        airport_out_info = airport_info[airport_out]
        airport_in_info = airport_info[airport_in]
        carrier_hotkey = EncodeAirline(carrier)
        data_row = carrier_hotkey+airport_out_info+airport_in_info+month
        train_set.append(data_row)
        y = int(any(df_airline[delay_type][k]>0 for delay_type in delay_types))
        label_train.append(y)
        
    return (train_set, label_train)
    
def EncodeCancelData(df_airline, airport_info):
    '''Change the dataframe to array of training set. The format of input feature is 
    [encoded_airline, lat, longtitude, elevation_ft, month-day] .
    
    @param df_airline: data frame of 
    @type airline: pd.DataFrame
    @param df_airline: airport information 
    @type airline: dict
    @return: train set and label
    @rtype: tuple of list
    '''
    
    train_set = []
    test_set = []
    label_train = []
    label_test = []
    N_data = len(df_airline)
    delay_types=['WEATHER_DELAY','CARRIER_DELAY','NAS_DELAY','SECURITY_DELAY','LATE_AIRCRAFT_DELAY']
    airline_set = {'F9':0, 'B6':1, 'EV':2, 'OO':3, 'UA':4, 'AA':5, 'WN':6, 'DL':7, 'HA':8, 'AS':9}
    for k in range(N_data):
        carrier = df_airline['OP_CARRIER'][k]
        if carrier not in airline_set: continue
        date = df_airline['FL_DATE'][k].split('-')
        month = [int(date[1]+date[2])]
        airport_out = df_airline['ORIGIN'][k]
        airport_in = df_airline['DEST'][k]
        airport_out_info = airport_info[airport_out]
        airport_in_info = airport_info[airport_in]
        carrier_hotkey = EncodeAirline(carrier)
        data_row = carrier_hotkey+airport_out_info+airport_in_info+month
        if len(data_row)<16: continue
        train_set.append(data_row)
        y = df_airline['CANCELLED'][k]
        label_train.append(y)
        
    return (train_set, label_train)
    
    
def GetAirportInfo():
    '''Get airport info from data and save them into dict.
    @return: airport information
    @rtype: dict
    '''
    
    df_airport = pd.read_csv('./data/airports.csv')
    airport_info = defaultdict(list)
    airline_name = {'9E':'Endeavor Air',
                    'AA':'American Airlines', 
                    'AS':'Alaska Airlines',
                    'B6':'JetBlue', 
                    'CO':'Continental Airlines', 
                    'DL':'Delta Air Lines', 
                    'EV':'Atlantic Southeast Airlines', 
                    'F9':'Frontier Airlines', 
                    'FL':'AirTran', 
                    'G4':'Allegiant Air',
                    'HA':'Hawaiian Airlines',
                    'MQ':'Envoy Air', 
                    'NK':'Spirit Airlines', 
                    'NW':'Northwest Airlines', 
                    'OH':'Comair',
                    'OO':'SKYWEST',
                    'UA':'United Airlines',
                    'US':'US Airways', 
                    'VX':'Virgin America', 
                    'WN':'Southwest Airlines',
                    'XE':'ExpressJet', 
                    'YV':'Mesa Airlines',
                    'YX':'Midwest Express', 
                   }

    hasiata = df_airport['iata_code'].notnull()
    for k in range(len(df_airport)):
        if not hasiata[k]: continue 
        iata = df_airport['iata_code'][k]
        elevation = df_airport['elevation_ft'][k] if df_airport['elevation_ft'][k]>0 else 0
        airport_info[iata] = [float(df_airport['latitude_deg'][k]),
                                float(df_airport['longitude_deg'][k]),
                                elevation]
    return airport_info

def ModifyDelayData(data_files):
    '''Read the raw data from data_files and convert them into ml training format.
     
    @param data_files: data files path
    @type data_files: list of str
    @return: None
    '''
 
    assert isinstance(data_files, list)
    
    airport_info = GetAirportInfo()
    for file_id in range(len(data_files)):
        print('File Name:', data_files[file_id])
        df_airline = pd.read_csv(data_files[file_id])
        if not os.path.exists('./data'):
            os.mkdir('./data')
        if not os.path.exists('./data/delay'):
            os.mkdir('./data/delay')
        mldata_path = './data/delay/train_set_%d.csv' %file_id
        data_set, label = EncodeDelayData(df_airline, airport_info)
        pd.DataFrame(data_set).to_csv(mldata_path)
        with open(mldata_path, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile, delimiter=',')
            for k, row in enumerate(data_set):
                csv_writer.writerow(row+[label[k]])
                
def ModifyCancelData(data_files):
    '''Read the raw data from data_files and convert them into ml training format.
     
    @param data_files: data files path
    @type data_files: list of str
    @return: None
    '''
    
    assert isinstance(data_files, list)
    airport_info = GetAirportInfo()
    for file_id in range(len(data_files)):
        print('File Name:', data_files[file_id])
        df_airline = pd.read_csv(data_airline[file_id])
        if not os.path.exists('./data'):
            os.mkdir('./data')
        if not os.path.exists('./data/cancel'):
            os.mkdir('./data/cancel')
        mldata_path = './data/cancel/train_set_%d.csv' %file_id
        data_set, label = EncodeCancelData(df_airline, airport_info)
        pd.DataFrame(data_set).to_csv(mldata_path)
        with open(mldata_path, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile,  delimiter=',')
            for k, row in enumerate(data_set):
                csv_writer.writerow(row+[label[k]])

def TrainDelayModel(model_path=None):
    '''Train delay prediction model. If model_path is not None, load the pre-trained
    model from model_path.
    @param model_path: folder to save model 
    @type model_path: str
    @return: tensorflow neural network
    @rtype: PredictModel class
    '''
    
    if model_path:
        delay_agent = PredictModel(17, model_path=model_path)
        return delay_agent
    else:
        # model initialization
        delay_agent = PredictModel(17)
        delay_agent.model.summary()

    # mini-batch training
    for epoch in range(100):
        file_id = epoch%10
        print('Total Epoch=', epoch)
        mldata_path = './data/delay/train_set_%d.csv' %file_id
        
        data_set = pd.read_csv(mldata_path, header=None)
        n_data = len(data_set)
        train_set = np.array(data_set.iloc[(n_data//10)*(epoch//10):(n_data//10)*(epoch//10+1),0:17])
        
        label = np.array(data_set.iloc[(n_data//10)*(epoch//10):(n_data//10)*(epoch//10+1),17])
        
        train_set = train_set[~np.isnan(label)]
        label = label[~np.isnan(label)]
        delay_agent.TrainModel(train_set, label, model_id=epoch, sub_epochs=1)
    return delay_agent
    
def TrainCancelModel():
    '''Train cancel prediction model. If model_path is not None, load the pre-trained
    model from model_path.
    @param model_path: folder to save model 
    @type model_path: str
    @return: tensorflow neural network
    @rtype: PredictModel class
    '''
    
    if model_path:
        cancel_agent = PredictModel(17, model_path=model_path)
        return cancel_agent
    else:
        # model initialization
        cancel_agent = PredictModel(17)
        cancel_agent.model.summary()

    # mini-batch training
    for epoch in range(100):
        file_id = epoch%10
        print('Total Epoch=', epoch)
        mldata_path = './data/cancel/train_set_%d.csv' %file_id
        
        data_set = pd.read_csv(mldata_path, header=None)
        n_data = len(data_set)
        train_set = np.array(data_set.iloc[(n_data//10)*(epoch//10):(n_data//10)*(epoch//10+1),0:17])
        
        label = np.array(data_set.iloc[(n_data//10)*(epoch//10):(n_data//10)*(epoch//10+1),17])
        
        train_set = train_set[~np.isnan(label)]
        label = label[~np.isnan(label)]
        cancel_agent.TrainModel(train_set, label, model_id=epoch, sub_epochs=1)

def TestModel(agent, mode='delay'):
    '''Get the tensorflow network. Test the model with 2018 flight data.
    
    @param agent: prediction model 
    @type agent: PredictModel 
    @param mode: predict is delay or cancel 
    @type mode: str
    @return: accuracy of prediction
    @rtype: float
    '''
    
    assert mode in ['delay', 'cancel']
    test_set_path = os.path.join('./data',mode,'train_set_9.csv')
    data_set = pd.read_csv(test_set_path, header=None)
    n_data = len(data_set)
    test_set = np.array(data_set.iloc[0:n_data,0:17])
    label = np.array(data_set.iloc[0:n_data,17])
    test_set = test_set[~np.isnan(label)]
    label = label[~np.isnan(label)]
    y_predict = np.argmax(agent.model.predict(test_set), axis=1)
    accuracy = sum(label==y_predict)/len(label)
    return accuracy
    
if __name__=='__main__':

    if len(sys.argv)<2:
        print('You should provide the mode!')
    mode = sys.argv[1]
    if mode=='modify_data':
        root = './data'
        data_files = []
        for i in range(10):
            data_files.append(root+'/'+str(2009+i)+'.csv')
        print('--- Modifying Data to Machine Learning Features ---')
        ModifyDelayData(data_files)
        ModifyCancelData(data_files)

    elif mode=='train':
        print('--- Training The Delay Model ---')
        delay_agent = TrainDelayModel()
        print('--- Training The Cancellation Model ---')
        cancel_agent = TrainCancelModel()

    elif mode=='test':
        print('--- Test Delay Model ---')
        try:
            delay_agent = TrainDelayModel('./model/delay/model_delay_99')
        except:
            delay_agent = TrainDelayModel()
        delay_accuracy = TestModel(delay_agent, mode='delay')
        print('Your delay model accuracy is %f' %delay_accuracy)

        print('--- Test Cancellation Model ---')
        try:
            cancel_agent = TrainDelayModel('./model/cancel/model_cancel_99')
        except:
            cancel_agent = TrainCancelModel()
        cancel_accuracy = TestModel(cancel_agent, mode='cancel')
        print('Your cancellation model accuracy is %f' %cancel_accuracy)

    else:
        print('MODE ERROR')
