import argparse
import math
import threading
import keyboard
import numpy as np
from pythonosc import dispatcher
from pythonosc import udp_client
from pythonosc import osc_server
from pythonosc import osc_message_builder
from pythonosc.osc_message_builder import OscMessageBuilder

class OscClient:
    def __init__(self,ip,port):
        self.ip = ip
        self.port = port
        # self.address = address
        parser = argparse.ArgumentParser()
        parser.add_argument("--ip", default=ip)
        parser.add_argument("--port", type=int, default=port)
        args = parser.parse_args()
        self.client = udp_client.SimpleUDPClient(args.ip, args.port)

    def sendMsg(self,msg,msgAdress):
        builder = OscMessageBuilder(address=msgAdress)
        for v in msg[0]: 
            builder.add_arg(v)
        out = builder.build()
        # print("sent osc message to",self.ip,"on port",self.port,"with address",self.address)
        self.client.send(out)

class OscServer:
    def getPred(self,unused_addr,arraynum,*args):
        if arraynum == 0:
            self.prePred = args
        if arraynum >= 1:
            self.prePred = np.vstack((self.prePred,args))
        if arraynum == 14:
            test = self.prePred.ravel()
            if(test.size == 11025):
                self.pred = test
                # print("P:",self.pred.size)
            # else:
                # print("Error Receiving P - Wrong Size")

    def getX(self,unused_addr, arraynum, *args):
        if arraynum == 0:
            self.prex = args
        if arraynum >= 1:
            self.prex = np.vstack((self.prex,args))
        if arraynum == 14:
            test = self.prex.ravel()
            if(test.size == 11025):
                self.xin = test
                print("X:",self.xin.size)
            else:
                print("Error Receiving X - Wrong Size")

    def getY(self,unused_addr, arraynum, *args):
        if arraynum == 0:
            self.prey = args
        if arraynum >= 1:
            self.prey = np.vstack((self.prey,args))
        if arraynum == 14:
            test = self.prey.ravel()
            if(test.size == 11025):
                self.yin = test
                print("Y:",self.yin.size)
            else:
                print("Error Receiving Y - Wrong Size")
    
    def addExample(self,unused_addr,*args):
        self.addexample = 1
    
    def delExample(self,unused_addr,*args):
        self.delexample = 1
    
    def delAll(self,unused_addr,*args):
        self.delall = 1
    
    def trainModel(self,unused_addr,*args):
        self.train = 1

    def trainNewModel(self,unused_addr,*args):
        self.trainNew = 1

    def close(self,unused_addr,*args):
        self.quit = 1

    def getEpochs(self,*args):
        self.epochs = args[1]
        print("Epochs:",self.epochs)
        
    def __init__(self,ip,port,xhandler,yhandler,predhandler):
        self.epochs = 1000
        self.addexample = 0
        self.delexample = 0
        self.delall = 0
        self.train = 0
        self.trainNew = 0
        self.quit = 0
        self.pred = np.array([0])
        self.xin = np.array([0])
        self.yin = np.array([0])
        self.prePred = np.array([0])
        self.prex = np.array([0])
        self.prey = np.array([0])
        self.xhandler = xhandler
        self.yhandler = yhandler
        self.predhandler= predhandler
        self.dispatcher = dispatcher.Dispatcher()
        self.dispatcher.map(xhandler, self.getX)
        self.dispatcher.map(yhandler,self.getY)
        self.dispatcher.map(predhandler,self.getPred)
        self.dispatcher.map('/keras/epochs',self.getEpochs)
        self.dispatcher.map('/keras/addExample',self.addExample)
        self.dispatcher.map('/keras/delExample',self.delExample)
        self.dispatcher.map('/keras/delAll',self.delAll)
        self.dispatcher.map('/keras/train',self.trainModel)
        self.dispatcher.map('/keras/trainNew',self.trainNewModel)
        self.dispatcher.map('/keras/quit',self.close)
        self.server = osc_server.ThreadingOSCUDPServer((ip, port), self.dispatcher)
        print("OSC server listening on {}".format(self.server.server_address),"with handlers:",self.xhandler,self.yhandler)
        server_thread = threading.Thread(target=self.server.serve_forever)
        server_thread.start()