import tornado.websocket
from tornado import gen
from tornado.ioloop import IOLoop
import sys
import signal
import json
import time
#import logging
import time
from multiprocessing import Queue
import os
import contextlib

#logging.basicConfig(filename='app.log',level=logging.DEBUG)


class WebSocketTimeoutException(Exception):
    pass


class WebSocketClient:
    def __init__(self,name,queue,config):
        """
        The constructor for WebSocketClient
 
        Parameters:
           config: Name of config file.
           queue: The message queue to process incoming messages.  
        """
        self.name = name
        try:
            self.config = config[self.name]
            self.url = self.config["endpoint"]
        except:
            raise AttributeError("Could not read config file")
 
        if "timeout" in self.config:
            self.timeout = self.config["timeout"]
        else:
            self.timeout  = None

        
        self.connection = None
        self.q = queue
    
    @gen.coroutine   
    def timeout_fn(self):
        print("One of the websockets is not responding, stopping IOLoop now")
        IOLoop.current().stop()

    def get_queue(self):
        return self.q

    @gen.coroutine
    def init_request(self):
        yield self.connection.write_message('ping')

    @gen.coroutine
    def process_output(self,message):
        yield self.q.put((self.name, message))

    @gen.coroutine
    def main(self):
        """
        Main loop of websocket client.
        """
        self.connection = yield tornado.websocket.websocket_connect(self.url)
        yield self.init_request()
        while True:
            if self.timeout:
                t = IOLoop.current().add_timeout(time.time() + self.timeout, self.timeout_fn)
            message = yield self.connection.read_message()
            try:
                message = json.loads(message)
            except json.decoder.JSONDecodeError:
                print("Received bad response: "+message)
                IOLoop.current().stop()
            yield self.process_output(message)
            if self.timeout:
                IOLoop.current().remove_timeout(t)


    def start(self):
        """
        Start the websocket client by calling main loop.
        """
        IOLoop.current().add_callback(self.main)


class CoinBaseClient(WebSocketClient):

    def __init__(self,name,queue,config):
        super().__init__(name,queue, config)
        try:
            self.init_commands = self.config["subscribe"]
            if "timeout" in self.config:
                self.timeout = self.config["timeout"]
            else:
                self.timeout  = None
        except KeyError:
            raise AttributeError("Could not read config file")



    @gen.coroutine
    def process_output(self,message):
        output = {}
        if(isinstance(message,(dict,)) and message["type"] == "l2update"):
            output["pair"] = message["product_id"].replace("-","")
            message = message["changes"]
            for item in message:
                output["type"] = "BID" if (item[0] == "buy") else "ASK"
                output["price"] = item[1]
                output["amount"] = item[2]
                yield self.q.put((self.name,output))
        else:
            #logging.debug("{} : {}".format(self.name,message))
            return

    @gen.coroutine
    def init_request(self):
        yield self.connection.write_message(json.dumps(self.init_commands))
        products = self.init_commands["product_ids"]
        while products:
            msg = yield self.connection.read_message()
            msg = json.loads(msg)
            try:
                if (msg["type"] == "snapshot") and (msg["product_id"] in products):
                    products.remove(msg["product_id"])
                else:
                    print("DEBUG ",msg)
                    continue
            except KeyError:
                print("Error: Could not parse socket output")
                exit(1)
            resp = {"type":"l2update","product_id":msg["product_id"],"changes":[]}
            for elem in msg["bids"]:
                resp["changes"].append(["buy"]+elem)
            yield self.process_output(resp)
            resp = {"type":"l2update","product_id":msg["product_id"],"changes":[]}
            for elem in msg["asks"]:
                resp["changes"].append(["sell"] + elem)
            yield self.process_output(resp)
        #logging.debug("Coinbase Init!")





class BitFinexClient(WebSocketClient):
    def __init__(self,name,queue,config):
        super().__init__(name,queue,config)
        self.name = "Bitfinex"
        try:
            self.init_commands = self.config["subscribe"]
            if "timeout" in self.config:
                self.timeout = self.config["timeout"]
            else:
                self.timeout  = None
            self.subscriptions = {}
        except KeyError:
            raise AttributeError("Could not read config file")

    @gen.coroutine
    def process_output(self,message):
        if message[1] == "hb":
            #logging.debug("{} : {}".format(self.name,message))
            return
        output = {}
        output["pair"] = self.subscriptions[message[0]]
        output["price"] = message[1]
        output["type"] = "BID" if (message[3] > 0) else "ASK"
        output["amount"] = 0 if message[2] == 0 else abs(message[3])
        yield self.q.put((self.name,output))

    @gen.coroutine
    def init_request(self):
        greeted = False
        while not greeted:
            try:
                greeting = yield self.connection.read_message()
                greeting = json.loads(greeting)
                assert greeting["event"] == "info"
                greeted = True
            except (KeyError, AssertionError) as e:
                raise AssertionError("Socket greeting is not valid")
            except TypeError:
                print("Error: No greeting received. Trying again.")
                continue

        for cmd in self.init_commands:
            #print("DEBUG CMD ",cmd)
            yield self.connection.write_message(json.dumps(cmd))

            while cmd["pair"] not in self.subscriptions.values():
                response = yield self.connection.read_message()
                response = json.loads(response)
                #print("DEBUG RESPONSE ",response)
                if (isinstance(response,(list,))):
                    yield self.process_output(response)
                    continue
                else:
                    try:
                        assert response["event"] == "subscribed"
                        assert response["channel"] == cmd["channel"]
                        assert response["pair"] == cmd["pair"]
                        assert response["freq"] == cmd["freq"]
                        self.subscriptions[response["chanId"]] = response["pair"]
                    except (KeyError, AssertionError) as e:
                        print("Error: Socket response not valid")
                        #todo stacktrace
                        os.exit(1)
                    snapshot = yield self.connection.read_message()
                    snapshot = json.loads(snapshot)
                    #print("DEBUG SNAPSHOT",snapshot)
                    for item in snapshot[1]:
                        yield self.process_output(([snapshot[0]] + item))
        #logging.debug("Bitfinex Init")
        