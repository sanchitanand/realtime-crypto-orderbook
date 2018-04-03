from websocketclient import WebSocketClient, BitFinexClient, CoinBaseClient
import json
from tornado.ioloop import IOLoop
import signal
from multiprocessing import Queue, Process
from tornado import gen
from db_insert_worker import DatabaseInsertWorker


db_string = "mysql://myapp:password@<your endpoint here>/mydb"   


def _stop():
    """
    Method to stop execution of IOLoop.
    """
    #print("\nReceived SIGINT, Shutting down now\n")
    #worker.stop()
    print("Stopping now , please wait for queue to finish.")
    IOLoop.current().stop()
    workers.join()
    q.close()





if __name__ == '__main__':
    q = Queue()
    _fd = open("websocketconfig.json")
    cfg = json.load(_fd)
    _fd.close()
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    workers = DatabaseInsertWorker(q,db_string=db_string,timeout=10, update_interval = 1)
    workers.start()
    signal.signal(signal.SIGINT, lambda x,y: IOLoop.current().add_callback_from_signal(_stop))
    ws = CoinBaseClient("Coinbase",q,cfg)
    ws.start()
    ws2 = BitFinexClient("Bitfinex",q,cfg)
    ws2.start()
    IOLoop.current().start()
