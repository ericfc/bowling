FROM python:3.6.5
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
ADD requirements.pip /code/
RUN pip install -r requirements.pip
ADD . /code/
