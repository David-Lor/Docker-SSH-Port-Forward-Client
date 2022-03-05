FROM python:3-alpine

ENV MAPPINGS="" \
    SSH_USER="" \
    SSH_HOST="" \
    SSH_PORT="22" \
    SSH_IPV6="0" \
    SSH_KEY_LOCATION="/ssh_key" \
    SSH_KEY_WRITE_LOCATION="/tmp/my_ssh_key" \
    SSH_COMPRESSION="0" \
    AUTOSSH="1" \
    AUTOSSH_PORT="0"

RUN apk --no-cache update && apk --no-cache add autossh

COPY entrypoint.py /

CMD ["python", "-u", "entrypoint.py"]
