FROM python:3-slim-buster

ARG USERNAME=user
ENV MAPPINGS="" \
    SSH_USER="" \
    SSH_HOST="" \
    SSH_PORT="22" \
    SSH_IPV6="0" \
    SSH_KEY_LOCATION="/ssh_key" \
    SSH_KEY_WRITE_LOCATION="/tmp/my_ssh_key"

RUN apt-get -yq update && \
    apt-get -yq install autossh && \
    rm -rf /var/lib/apt/lists/*

RUN useradd -ms /bin/bash $USERNAME
USER $USERNAME
WORKDIR /home/$USERNAME

COPY entrypoint.py ./

CMD ["python", "-u", "entrypoint.py"]
