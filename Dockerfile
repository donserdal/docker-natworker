FROM python:alpine

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY flaskscript.py ./

EXPOSE 5000/tcp

CMD [ "python", "./flaskscript.py" ]
