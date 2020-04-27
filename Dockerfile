FROM python:3

MAINTAINER Daniel Siepmann
LABEL Description="This image should provide environment to lint neotags" Vendor="DanielSiepmann" Version="1.0"

# Install dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir pycodestyle==2.5.0 pynvim pyfakefs==3.1
