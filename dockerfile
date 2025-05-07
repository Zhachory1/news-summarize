FROM python:3.9.4

WORKDIR /app

COPY third_party/requirements.txt ./

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

EXPOSE 8080:5000

RUN apt-get update \
 && apt-get install

RUN pip install -r requirements.txt

COPY . .

CMD ["python", "wsgi.py"]
