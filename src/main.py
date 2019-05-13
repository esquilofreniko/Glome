import keras1
import numpy as np
import time
import argparse
import math
import keyboard
from osc import OscClient
from osc import OscServer
from keras1 import NeuralNetRegression

#parameters
inputdimension  = 11025
outputdimension = 11025
nHidden = 3
nNodes = 10
epochs = 1000

trained = 0
nExamples = 0
x = np.array([0])
y = np.array([0])
nn = NeuralNetRegression(np.zeros((1,11025)),np.zeros((1,11025)),nHidden,nNodes)
oscclient = OscClient("127.0.0.1",12000)
oscclient.sendMsg(np.array([[0],[0]]).tolist(),'/keras/training')
oscserver = OscServer("127.0.0.1",6448,'/keras/Xin','/keras/Yin')
print("press \+q: quit")

while True:
    time.sleep(0.1)
    if trained == 1:
        xin = np.array([oscserver.xin])
        if(xin.shape[1] == 11025):
            yout = nn.predict(xin)
            yout = yout.tolist()
            oscclient.sendMsg(yout,'/keras/Yout')
            oscserverxin = oscserver.xin
    # try: 
    if keyboard.is_pressed('\+q'): 
        oscserver.server.shutdown()
        quit()
        break
    elif oscserver.addexample == 1:
        if(oscserver.xin.size == 11025 & oscserver.yin.size == 11025):
            if(nExamples==0):
                x = oscserver.xin
                y = oscserver.yin
            else:
                x = np.vstack((x,oscserver.xin))
                y = np.vstack((y,oscserver.yin))
            nExamples += 1
            print("nExamples:", nExamples)
        else:
            print("Error Adding Example - Wrong Size")
        oscserver.addexample = 0
        pass
    elif oscserver.delexample == 1:
        nExamples -= 1
        x = x[:-1]
        y = y[:-1]
        print(x)
        print(y)
        if(nExamples<0):nExamples=0
        print("Removed Example")
        print("nExamples:", nExamples)
        oscserver.delexample = 0
        pass
    elif oscserver.delall == 1:
        nExamples = 0
        x = np.array([0])
        y = np.array([0])
        print("Cleared Examples")
        print("nExamples:", nExamples)
        oscserver.delall = 0
    elif oscserver.train == 1:
        # train
        if(nExamples > 1):
            oscclient.sendMsg(np.array([[1],[1]]).tolist(),'/keras/training')
            print("Training Neural Network...")
            print("nExamples:",nExamples,"Epochs:",oscserver.epochs)
            nn.train(x,y,nExamples,oscserver.epochs)
            print("Finished Training Neural Network")
            oscclient.sendMsg(np.array([[0],[0]]).tolist(),'/keras/training')
            trained = 1
            oscserver.train = 0
        else:
            print("Error Training - Not Enough Examples.")
            oscserver.train = 0
        pass
    elif oscserver.trainNew == 1:
        # train New
        if(nExamples > 1):
            nn = NeuralNetRegression(x,y,nHidden,nNodes)
            print("Training New Neural Network...")
            print("nExamples:",nExamples,"Epochs:",oscserver.epochs)
            oscclient.sendMsg(np.array([[1],[1]]).tolist(),'/keras/training')
            nn.train(x,y,nExamples,oscserver.epochs)
            print("Finished Training New Neural Network")
            oscclient.sendMsg(np.array([[0],[0]]).tolist(),'/keras/training')
            trained = 1
            oscserver.trainNew = 0
        else:
            print("no Examples found. Need atleast 2 Examples to Train")
            oscserver.trainNew = 0
        pass
    if oscserver.quit == 1:
        oscserver.server.shutdown()
        quit()
        break
    else:
        pass
    # except:
        # oscserver.server.shutdown()
        # quit()
        # break