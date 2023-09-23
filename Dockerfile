FROM python:3.11

WORKDIR /code

COPY . /code

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

RUN chmod 755 /code/start.sh

CMD ["sh", "start.sh"]