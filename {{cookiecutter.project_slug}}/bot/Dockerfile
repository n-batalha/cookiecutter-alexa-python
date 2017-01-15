FROM python:2
MAINTAINER Nelson Batalha <nelson.batalha@gmail.com>

COPY requirements.txt /tmp/requirements.txt

# Docker will cache this
RUN pip install -U pip && \
    pip --exists-action s install -r /tmp/requirements.txt

RUN ["mkdir", "-p", "/srv/logs"]

WORKDIR /app

EXPOSE 8088

ENV API_PORT "8088"

COPY . /app/

ENTRYPOINT ["./docker-entrypoint.sh"]
