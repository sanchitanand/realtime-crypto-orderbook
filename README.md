<<<<<<< HEAD
# realtime-crypto-feed
=======
This is a sample project to aggregate order book information from multiple feeds. The project is split into three docker containers. docker_ws_client is a websocket client which pulls feeds and inserts into the table. docker_ws_api_server is a websocket and rest endpoint which queries the database. docker_angular_frontend servers the webpage.


Instructions to start project: 
1. Run init.sql on database (It creates a new database,user,table and stored procedures)
2. Go to docker_ws_client/ws_client/main.py and modify db_string (Change hostname)
3. Modify websocketconfig.json located in the same directory, or leave it as is. Each websocket has an endpoint, a timeout parameter (optional), and a subscribe command. 
4. Go to docker_ws_api_server/app/apihandler.py and modify db_string.
5. Go to docker_angular_app/angular_frontend/assets/app.js and modify the websocket endpoint (This is the endpoint from ws_client container).
6. Build all the dockerfiles and run them. Start with ws_client.

Known Issues:
1. The websocket client sometimes hangs on an unresponsive websocket. Make sure to use timeout, and restart service.
2. The snapshot updates from ws_api_server are quite error prone unless you use REPEATABLE READ.
3. If multiple entries for the same price exist from multiple sources (ex. Coinbase and Bitfinex), the query_update call will attempt to merge the sizes. It returns the combined size, but it unfortunately returns the row twice.
4. General database bloat. Suggest deleting entries with size 0 if they are not updated for a while.
>>>>>>> initial
