FROM python:3.10-alpine 
WORKDIR /Job_Portal 
ADD . /Job_Portal
COPY requirements.txt . 
RUN pip install -r requirements.txt  
CMD ["python","app.py"]