# Use the Python 3.10 image as the base image
FROM python:3.10

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV GECKODRIVER_VER=v0.33.0
ENV FIREFOX_VER=116.0

# Update and install necessary packages
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y \
    firefox-esr \
    curl \
    libx11-xcb1 \
    libdbus-glib-1-2 \
    vim \
    nano && \
    pip install \
    requests \
    selenium \
    progress

# Download and install the latest Firefox
RUN curl -sSLO https://download-installer.cdn.mozilla.net/pub/firefox/releases/${FIREFOX_VER}/linux-x86_64/en-US/firefox-${FIREFOX_VER}.tar.bz2 && \
    tar -jxf firefox-* && \
    mv firefox /opt/ && \
    chmod 755 /opt/firefox && \
    chmod 755 /opt/firefox/firefox

# Download and install geckodriver
RUN curl -sSLO https://github.com/mozilla/geckodriver/releases/download/${GECKODRIVER_VER}/geckodriver-${GECKODRIVER_VER}-linux64.tar.gz && \
    tar zxf geckodriver-*.tar.gz && \
    mv geckodriver /usr/bin/

# Set the working directory
WORKDIR /hd_script

# Clone a Git repository into the working directory
RUN git clone https://github.com/amarana-te/PS-E-078526-EAS_Config.git .
