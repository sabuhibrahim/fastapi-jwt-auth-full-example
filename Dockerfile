FROM python:3.11

WORKDIR /code

COPY ./requirements.txt ./requirements.txt 

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . .

RUN chmod 755 /code/start.sh

CMD ["sh", "start.sh"]