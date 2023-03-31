#FROM python:3.10-slim-buster
FROM 026389300232.dkr.ecr.eu-central-1.amazonaws.com/cruddur-python:3.10-slim-buster

# Inside Container
WORKDIR /backend-flask

# Outside Container -> Inside Container
COPY requirements.txt requirements.txt

# Inside Container
RUN pip3 install -r requirements.txt

# Outside Container -> Inside Container
COPY . .

# Inside Container
#ENV FLASK_ENV=development
ENV FLASK_DEBUG=1

EXPOSE ${PORT}

#CMD python3 -m flask run --host=0.0.0.0 --port=4567
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0", "--port=4567"]
