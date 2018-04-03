from sqlalchemy import create_engine
from sqlalchemy.sql import text
from multiprocessing import Process, Lock
import os
import time 
import queue

def execute_stored_procedure(engine,sp_name,args):
	connection = engine.raw_connection()
	cursor = connection.cursor()
	cursor.callproc(sp_name,args)
	results = list(cursor.fetchall())
	cursor.close()
	connection.commit()
	connection.close()
	return results


class DatabaseInsertWorker:
	def __init__(self,job_queue,db_string="mysql://myapp:password@localhost/mydb",timeout =30, update_interval = 0.5):
		print("Parent thread ",os.getpid())
		self.engine = create_engine(db_string)
		self.job_queue = job_queue
		self.insert_or_update  = text("INSERT into order_book (type, source, pair, price, size ) values (:type, :source, :pair, :price, :size) ON DUPLICATE KEY UPDATE size = VALUES(size);") 
		self.timeout= timeout
		self.update_interval = update_interval
	def start(self):
		self.proc = Process(target=self.run)
		self.proc.start()

	def join(self):
		self.proc.join()
		self.engine.dispose()

	def run(self):
		print("Starting worker thread on ",os.getpid())
		current = []
		start_time = time.time()
		while True:
			if current and time.time() - start_time > self.update_interval:
				with self.engine.connect() as conn:
					trans = conn.begin()
					try:
						conn.execution_options(autocommit=False).execute(self.insert_or_update,current)
						trans.commit()
						start_time = time.time()
						current = []
					except Exception as e:
						trans.rollback()
						print(current)
						raise e

			else:
				try:
					next = self.job_queue.get(block = True, timeout = self.timeout)
				except queue.Empty as e:
					break
				my_dict = {}
				my_dict["source"] = next[0]
				my_dict["pair"] = next[1]["pair"]
				my_dict["type"] = next[1]["type"]
				my_dict["price"] = next[1]["price"]
				my_dict["size"] = next[1]["amount"]
				current.append(my_dict)
		print("Timeout exceeded, stopping worker on",os.getpid())


