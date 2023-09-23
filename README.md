# FastAPI JWT Authentication example

This project includes authentication APIs (login, register, verify, forgot-password, reset-password, update-password) and article list and create APIs. It uses an async PostgreSQL connection with SqlAlchemy ORM. There is an alembic config also.

## Installation
- If you want to run docker you need to [install docker](https://docs.docker.com/engine/install/)
- Configure your postgresql
- Create .env from .env.example
```bash
cp .env.example .env
```
- Add Postgresql config to .env
- Run docker
```bash
docker-compose up -d --build
```
or
```bash
docker compose up -d --build
```
### if you want to run this app without docker
- Add Postgresql config to alembic/env.py and src/core/config.py
- Use the package manager [pip](https://pip.pypa.io/en/stable/) to install requirements.txt.
```bash
pip install -r requirements.txt
```
- Run app with start.sh. It will do migrate migrations then run app 
```bash
chmod 755 start.sh
sh start.sh
```