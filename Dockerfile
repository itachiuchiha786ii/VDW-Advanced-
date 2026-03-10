FROM python:3.10

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD [gunicorn, --bind, 0.0.0.0:5000, app:app]
