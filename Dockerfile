# Name: pwtgbot Dockerfile
# Creator: K4YT3X
# Date Created: June 20, 2021
# Last Modified: June 20, 2021

# using Alpine Linux for its small size
FROM alpine:3.14.0

# file mainainter labels
LABEL maintainer="K4YT3X <k4yt3x@k4yt3x.com>"

# install pwtgbot on Alpine
RUN apk add --no-cache --virtual .rundeps \
        py3-pip \
        py3-cryptography \
        py3-openssl \
    && apk add --no-cache --virtual .build-deps \
        build-base \
        libffi-dev \
        python3-dev \
    && pip install -U pwtgbot \
    && apk del .build-deps

WORKDIR /
ENTRYPOINT ["/usr/bin/pwtgbot"]