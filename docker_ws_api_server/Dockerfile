FROM python:3.6.4
RUN apt-get update && apt-get install -y python-mysqldb
COPY ./requirements.txt /home/app/requirements.txt
WORKDIR /home/app
RUN pip install -r requirements.txt
EXPOSE 80
COPY ./app .
CMD ["python","./apihandler.py"]

