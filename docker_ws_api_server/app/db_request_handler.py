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


class DatabaseRequestHandler:
	def __init__(self,db_string="mysql://myapp:password@localhost/mydb", query_snapshot="query_snapshot",query_update="query_update",query_pairs="query_pairs",query_date = "query_date"):
		self.engine = create_engine(db_string,isolation_level = "REPEATABLE READ")
		self.sp_query_pairs = query_pairs
		self.sp_query_snapshot = query_snapshot
		self.sp_query_update = query_update
		self.sp_query_date = query_date

	def query_pairs(self):
		results = execute_stored_procedure(self.engine,self.sp_query_pairs,[])
		return [row[0] for row in results]

	def query_date(self):
		results = execute_stored_procedure(self.engine,self.sp_query_date,[])
		return results[0][0];

	def query_db(self,pair,exchange=None,min_price=0,max_price= 3.402823466e+38):
		results = execute_stored_procedure(self.engine, self.sp_query_snapshot, [exchange,pair,min_price,max_price])
		results_dict = [{"source":row[0],"pair":row[1],"type":row[2],"price":row[3],"size":row[4],"last_update":row[5]} for row in results]
		return results_dict

	def query_db_ws(self,pair,last_query=None):
		query = execute_stored_procedure(self.engine, self.sp_query_update, [pair,last_query])
		if query:
			new_date = max([row[4] for row in query])
			results = [new_date]+ [list(row[1:4]) for row in query]
			return results
		else:
			return None

	def close():
		self.engine.dispose()


