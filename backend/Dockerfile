FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && apt-get install -y git

RUN pip install -r requirements.txt --no-cache-dir

COPY . .

LABEL author='Larkin Michael'

RUN chmod +x docker-entrypoint.sh

ENTRYPOINT ["./docker-entrypoint.sh"]
