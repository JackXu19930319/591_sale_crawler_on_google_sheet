FROM python:3.11-alpine
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
#EXPOSE 8888
CMD python main.py
