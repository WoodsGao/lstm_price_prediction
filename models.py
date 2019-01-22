from keras.layers.core import Dense, Activation, Dropout
from keras.layers.recurrent import LSTM
from keras.models import Sequential
from keras.layers.convolutional import Conv1D
from keras.layers.convolutional import MaxPooling1D
import time
import json
import numpy as np
import tensorflow as tf
from keras.models import load_model
import os, sys
import keras.backend.tensorflow_backend as KTF
from threading import Thread

# os.chdir(sys.path[0])
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ["CUDA_VISIBLE_DEVICES"] = '0'
# config = tf.ConfigProto()
# # config.gpu_options.allow_growth = True  # 不全部占满显存, 按需分配
# sess = tf.Session(config=config)
# KTF.set_session(sess)

class StockLSTM():

    def __init__(self, stock, run_interval):
        self.timestamp_interval = 15*60
        self.train_len = 7*24*3600//self.timestamp_interval
        self.pre_len = 24*3600//self.timestamp_interval
        self.test_len = 7*self.pre_len
        self.batch_size = 32
        self.run_interval = run_interval
        self.stock = stock
        # self.model = self.build_model()

    def build_model(self):
        model = Sequential()
        model.add(LSTM(input_dim=1,
                    output_dim=self.test_len,
                    return_sequences=True))
        model.add(Dropout(0.2))
        model.add(Conv1D(filters=32, kernel_size=3, padding='same', activation='relu'))
        model.add(MaxPooling1D(pool_size=2))
        model.add(LSTM(100,
                    return_sequences=False))
        model.add(Dropout(0.2))
        model.add(Dense(output_dim=1))
        model.add(Activation('linear'))
        model.compile(loss='mse', optimizer='adam')
        return model


    def lstm_predict(self):
        try:
            with open('now/%s' % self.stock, 'r') as f:
                origin = json.loads(f.read())
            data = [o[1] for o in origin]
            timestamp = [o[0] for o in origin]
            max_data = max(data)
            min_data = min(data)
            if max_data == min_data:
                return 0
            data = [(d-min_data)/(max_data-min_data) for d in data]
            # data = [origin[i]/origin[i-1] for i in range(1, len(origin))]

            x = []
            y = []
            for i in range(len(data)-self.pre_len-self.test_len):
                x.append(data[i:i+self.test_len])
                y.append(data[i+self.pre_len+self.test_len])
            x = np.array(x).reshape(-1,self.test_len,1)
            y = np.array(y).reshape(-1,1)
            print(x.shape,y.shape)

            model = self.build_model()
            model.fit(x, y ,batch_size=self.batch_size,epochs=100,validation_split=0.05)

            x = []
            for i in range(len(data)-self.test_len):
                x.append(data[i:i+self.test_len])
            x = np.array(x).reshape(-1,self.test_len,1)
            print(x.shape)

            pre = model.predict(x, batch_size=self.batch_size).reshape(-1).tolist()
            pre = [p*(max_data-min_data)+min_data for p in pre]
            pre = [[timestamp[i]+(self.pre_len+self.test_len)*self.timestamp_interval, float(p)] for i, p in enumerate(pre)]
            with open('pre/%s' % self.stock, 'w') as f:
                f.write(json.dumps(pre))
            return 1
        except Exception as e:
            print(e)
            return 0

    def run_thread(self):
        while 1:
            if self.lstm_predict():
                time.sleep(self.run_interval)
            else:
                time.sleep(60)
    
    def run(self):
        t = Thread(target=self.run_thread)
        t.setDaemon(True)
        t.start()


if __name__ == "__main__":
    a = StockLSTM('xbtusd', 60*60)
    a.run()
    input()
