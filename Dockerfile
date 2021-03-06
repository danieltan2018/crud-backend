FROM python:3.8
EXPOSE 80
WORKDIR /WORKDIR
COPY requirements.txt /WORKDIR
RUN pip install -r requirements.txt
COPY app.py /WORKDIR
CMD python app.py