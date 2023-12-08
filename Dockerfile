FROM tiangolo/uwsgi-nginx-flask:python3.11

LABEL maintainer="Rahul Kataria <rahulkataria3355@gmail.com>"

ADD ./requirements.txt /requirements.txt
RUN pip install --upgrade pip && \
    pip install -r /requirements.txt 

RUN apt-get -y update
RUN apt-get install -y build-essential
RUN apt-get install -y poppler-utils
COPY ./app /app
WORKDIR /app
EXPOSE 80