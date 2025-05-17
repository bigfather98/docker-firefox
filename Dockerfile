FROM alpine:3.14 AS membarrier
WORKDIR /tmp
COPY membarrier_check.c .
RUN apk --no-cache add build-base linux-headers
RUN gcc -static -o membarrier_check membarrier_check.c
RUN strip membarrier_check

FROM jlesage/baseimage-gui:alpine-3.21-v4.7.1

ARG DOCKER_IMAGE_VERSION=
ARG FIREFOX_VERSION=136.0.4-r0 # Or your preferred Firefox version

WORKDIR /tmp

RUN \
     add-pkg firefox=${FIREFOX_VERSION}

RUN \
    add-pkg \
        mesa-dri-gallium \
        libpulse \
        adwaita-icon-theme \
        font-dejavu \
        xdotool \
        python3 \
        py3-pip \
        tcl-dev \
        tk-dev \
        python3-dev \
        scrot \
        build-base \
        && \
    python3 -m pip install --upgrade pip --break-system-packages && \
    pip3 install --no-cache-dir --break-system-packages Flask pyautogui && \
    find /usr/share/icons/Adwaita -type d -mindepth 1 -maxdepth 1 -not -name 16x16 -not -name scalable -exec rm -rf {} ';' && \
    true

RUN \
    APP_ICON_URL=https://github.com/jlesage/docker-templates/raw/master/jlesage/images/firefox-icon.png && \
    install_app_icon.sh "$APP_ICON_URL"

COPY rootfs/ / # This should copy your mouse_controller.py into /opt/mouse-controller/ if structured correctly
COPY --from=membarrier /tmp/membarrier_check /usr/bin/

EXPOSE 5001

# s6-overlay service definition for the mouse controller API
RUN \
    mkdir -p /etc/s6-overlay/s6-rc.d/mouse-controller && \
    echo '#!/usr/bin/with-contenv bash' > /etc/s6-overlay/s6-rc.d/mouse-controller/run && \
    echo 'source /etc/s6/services/init/load-env.sh' >> /etc/s6-overlay/s6-rc.d/mouse-controller/run && \
    echo 'echo "Mouse Controller Service: Attempting to start Mouse Controller API..."' >> /etc/s6-overlay/s6-rc.d/mouse-controller/run && \
    echo 'echo "Mouse Controller Service: Listing /opt/mouse-controller/ contents:"' >> /etc/s6-overlay/s6-rc.d/mouse-controller/run && \
    echo 'ls -la /opt/mouse-controller/' >> /etc/s6-overlay/s6-rc.d/mouse-controller/run && \
    echo 'echo "Mouse Controller Service: Python3 version:"' >> /etc/s6-overlay/s6-rc.d/mouse-controller/run && \
    echo 'python3 --version' >> /etc/s6-overlay/s6-rc.d/mouse-controller/run && \
    echo 'echo "Mouse Controller Service: Pip3 version:"' >> /etc/s6-overlay/s6-rc.d/mouse-controller/run && \
    echo 'pip3 --version' >> /etc/s6-overlay/s6-rc.d/mouse-controller/run && \
    echo 'echo "Mouse Controller Service: Checking for pyautogui import:"' >> /etc/s6-overlay/s6-rc.d/mouse-controller/run && \
    echo 'python3 -c "import pyautogui; print(pyautogui.__version__)"' >> /etc/s6-overlay/s6-rc.d/mouse-controller/run || echo "Mouse Controller Service: PyAutoGUI import check failed (this command might error if pyautogui has issues)"' >> /etc/s6-overlay/s6-rc.d/mouse-controller/run && \
    echo 'echo "Mouse Controller Service: Executing python script /opt/mouse-controller/mouse_controller.py ..."' >> /etc/s6-overlay/s6-rc.d/mouse-controller/run && \
    echo 'exec s6-setuidgid "${USER_ID}:${GROUP_ID}" python3 /opt/mouse-controller/mouse_controller.py' >> /etc/s6-overlay/s6-rc.d/mouse-controller/run && \
    chmod +x /etc/s6-overlay/s6-rc.d/mouse-controller/run && \
    echo "longrun" > /etc/s6-overlay/s6-rc.d/mouse-controller/type && \
    mkdir -p /etc/s6-overlay/s6-rc.d/mouse-controller/dependencies.d

RUN \
    set-cont-env APP_NAME "Firefox" && \
    set-cont-env APP_VERSION "$FIREFOX_VERSION" && \
    set-cont-env DOCKER_IMAGE_VERSION "$DOCKER_IMAGE_VERSION" && \
    set-cont-env MOUSE_API_PORT "5001" && \
    true

ENV \
    FF_OPEN_URL= \
    FF_KIOSK=0 \
    FF_CUSTOM_ARGS=

LABEL \
      org.label-schema.name="firefox-with-mousecontrol" \
      org.label-schema.description="Docker container for Firefox with integrated mouse control API" \
      org.label-schema.version="${DOCKER_IMAGE_VERSION:-unknown}" \
      org.label-schema.vcs-url="https://github.com/bigfather98/docker-firefox" \
      org.label-schema.schema-version="1.0"
