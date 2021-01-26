FROM python:3.6.7-alpine3.6
RUN apk update && apk add gcc libc-dev make git libffi-dev python3-dev libxml2-dev libxslt-dev musl-dev linux-headers g++
WORKDIR /code
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8050
CMD ["python", "./app.py"]