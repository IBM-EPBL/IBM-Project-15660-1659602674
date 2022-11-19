FROM python:3.6.0
WORKDIR kannakar
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .
CMD [ "python3", "-m" , "flask", "run"]
