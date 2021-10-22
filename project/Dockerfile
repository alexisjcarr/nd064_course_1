FROM python:3.7

COPY ./techtrends/requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install -r requirements.txt

COPY ./techtrends /app

RUN python init_db.py

ENTRYPOINT [ "python" ]

CMD ["app.py"]

EXPOSE 7111
