from datetime import date, datetime, timedelta
import tornado.escape
from tornado.ioloop import IOLoop,PeriodicCallback
import tornado.web
import tornado.websocket
from db_request_handler import DatabaseRequestHandler
from tornado import gen
import json
import sys



db_string = "mysql://myapp:password@<your endpoint here>/mydb"    

class UpdateGenerator:
    def __init__(self,interval = 1):
        self.dbhandler = DatabaseRequestHandler(db_string = db_string)
        self.pairs = self.dbhandler.query_pairs()
        self.subscriptions = {pair:[] for pair in self.pairs}
        last_date = self.dbhandler.query_date()
        self.last_query = {pair:last_date for pair in self.pairs}
        PeriodicCallback(self.update,interval*1000).start()

    @gen.coroutine
    def subscribe(self,socket,pair):
        if pair not in self.subscriptions:
            print("Error: pair ",pair, " does not exist")
            yield socket.write_message("Error: Bad request")
            return
        if socket in self.subscriptions[pair]:
            print("Already subscribed to pair")
            return
        results = self.dbhandler.query_db_ws(pair)
        message = {"event":"subscribed","pair":pair,"changes":results[1:]}
        try:
            yield socket.write_message(json.dumps(message))
            print("Success, socket subscribed to ",pair)
            self.subscriptions[pair].append(socket)
        except tornado.websocket.WebSocketClosedError:
            print("Something went wrong here subscribe")
            raise e

    @gen.coroutine
    def update(self):
        for pair in self.subscriptions.keys():
            print("query date: ",self.last_query[pair])
            results = self.dbhandler.query_db_ws(pair, last_query = self.last_query[pair])
            if not results:
                update = {"event":"hb","pair":pair}
            else:   
                update = {"event":"update","pair":pair,"changes":results[1:]}
                self.last_query[pair] = results[0]
            for socket in self.subscriptions[pair]:
                try:
                    yield socket.write_message(update)
                except tornado.websocket.WebSocketClosedError as e:
                    print("Something went wrong here")
                    raise e

    def unsubscribe(self,socket):
        for pair in self.subscriptions.keys():
            try:
                self.subscriptions[pair].remove(socket)
                print("Unsubscribed socket from ",pair)
            except ValueError:
                pass


class GetWebSocketHandler(tornado.websocket.WebSocketHandler):
    def check_origin(self,origin):
        return True

    @gen.coroutine
    def on_message(self,message):
        message = json.loads(message)
        if "event" in message and message["event"] == "subscribe" and "pair" in message and message["pair"] in updater.pairs:
            print("Received subscription request for ",message["pair"])
            yield updater.subscribe(self,message["pair"])
        else:
            print("Received bad request")
            yield self.write_message("Error: Invalid Request")

    def on_close(self):
        print("Socket disconnected")
        updater.unsubscribe(self)


class GetSnapshotHandler(tornado.web.RequestHandler):
    def get(self):
        pair = self.get_argument("pair",None)
        if not pair:
            raise tornado.web.HTTPError(400)
        exchange = self.get_argument("exchange",None)
        min_price = float(self.get_argument("min",0))
        max_price = float(self.get_argument("max",3.402823466e+38))
        print(pair,exchange,min_price,max_price)
        results = updater.dbhandler.query_db(pair,exchange=exchange,min_price=min_price,max_price=max_price)
        for row in results:
            row["last_update"] = row["last_update"].strftime('%Y-%m-%dT%H:%M:%S')
        self.write("\n".join([row.__repr__() for row in results]))
 
application = tornado.web.Application([
    (r"/snapshot", GetSnapshotHandler),
    ("/websocket",GetWebSocketHandler)
])
 
if __name__ == "__main__":
    updater = UpdateGenerator()
    application.listen(8080)
    IOLoop.current().start()