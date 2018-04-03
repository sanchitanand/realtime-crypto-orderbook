FROM python:3.6.4
RUN apt-get update && apt-get install -y python-mysqldb
COPY ./requirements.txt /home/ws_client/requirements.txt
WORKDIR /home/ws_client
RUN pip install -r requirements.txt
COPY ./ws_client .
CMD ["python","./main.py"]

