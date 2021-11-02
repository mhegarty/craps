FROM python:3.8
LABEL maintainer "Mike Hegarty <mike@petorca.com>"
RUN pip install craps dask distributed bokeh joblib