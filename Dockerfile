FROM alpine:3.5

MAINTAINER Daniel Siepmann
LABEL Description="This image should provide environment to lint neotags" Vendor="DanielSiepmann" Version="1.0"

RUN apk update && apk upgrade

# Install dependencies
RUN apk add python3 py-pip

# Clean APK cache
RUN rm -rf /var/cache/apk/*

# Install dependencies
RUN pip install pep8 neovim
