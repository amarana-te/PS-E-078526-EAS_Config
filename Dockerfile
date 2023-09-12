FROM python:3.10
 
ENV DEBIAN_FRONTEND noninteractive
ENV GECKODRIVER_VER v0.33.0
ENV FIREFOX_VER 116.0
 
RUN set -x \
   && apt update \
   && apt upgrade -y \
   && apt install -y \
        firefox-esr \
        curl \
        libx11-xcb1 \
       libdbus-glib-1-2 \
   && pip install  \
       requests \
       selenium \ 
       progress 
 
# Add latest FireFox
RUN set -x \
   && curl -sSLO https://download-installer.cdn.mozilla.net/pub/firefox/releases/${FIREFOX_VER}/linux-x86_64/en-US/firefox-${FIREFOX_VER}.tar.bz2 \
   && tar -jxf firefox-* \
   && mv firefox /opt/ \
   && chmod 755 /opt/firefox \
   && chmod 755 /opt/firefox/firefox
  
# Add geckodriver
RUN set -x \
   && curl -sSLO https://github.com/mozilla/geckodriver/releases/download/${GECKODRIVER_VER}/geckodriver-${GECKODRIVER_VER}-linux64.tar.gz \
   && tar zxf geckodriver-*.tar.gz \
   && mv geckodriver /usr/bin/
  
WORKDIR /hd_script
 
RUN git clone https://github.com/amarana-te/PS-E-078526-EAS_Config.git . 