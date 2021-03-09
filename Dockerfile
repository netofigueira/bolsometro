FROM python:3.8

RUN apt-get update
#copy application code
WORKDIR /BOLSOMETRO
COPY . .
COPY requirements.txt .

#fetch app specific dependencies

RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt


EXPOSE 5000
#ENTRYPOINT ['python3']

#CMD [ "bolsometro_stream.py" ]
#Expose port

#EXPOSE 5000

#start app

#CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]
