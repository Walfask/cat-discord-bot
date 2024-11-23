FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt requirements.txt
COPY src src

RUN pip install -r requirements.txt
CMD ["python3", "src/cat_bot.py"]
