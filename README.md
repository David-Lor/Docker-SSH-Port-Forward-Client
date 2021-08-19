# Docker SSH Port Forward Client

[![Docker Hub](https://img.shields.io/badge/%20-DockerHub-blue?logo=docker&style=plastic)](https://hub.docker.com/r/davidlor/ssh-port-forward-client)
![Docker Image Size (latest by date)](https://img.shields.io/docker/image-size/davidlor/ssh-port-forward-client?sort=date&style=plastic)

Container to connect to a remote SSH server and forward one or more remote TCP ports.
Image based on python:3-slim-buster, using autossh for SSH connection.

**This image is experimental and might have undesirable effects. Use it under your responsability!**

## Getting started

*Make sure your SSH server is configured properly to allow TCP port forwarding*

- The following example will forward port `80` from remote host to port `8080` on local container, which is finally exposed.
- The remote host is `192.168.0.100`, with a SSH server available at default port 22 with user `foo`.
- A SSH private key without password protection is required to connect to the remote server with the given user, and is bind mounted on `/ssh_key` path inside the container.

```bash
docker run -d --name=ssh_portforward \
  -e "MAPPINGS=8080:127.0.0.1:80" \
  -e "SSH_HOST=192.168.0.100" \
  -e "SSH_USER=foo" -p 8080:8080 \
  -v "/home/user/ssh_key:/ssh_key:ro" \
  davidlor/ssh-port-forward-client:dev
```

Now, port 80 of remote host should be accesible from port 8080 within and without the container.

## Configuration

Currently, the settings are provided through environment variables, which are the following:

### Mappings

**MAPPINGS** is the most important environment variable. Is where we define the relation of local & remote bind hosts & ports to forward to and from.

Each mapping must have at least 1 argument and at most 4 arguments, split by `:`. The arguments are: `LOCAL_HOST:LOCAL_PORT:REMOTE_HOST:REMOTE_PORT`, being:

- `REMOTE_PORT`: port on remote machine to forward through SSH (the only argument required)
- `REMOTE_HOST`: host on remote network to forward the `REMOTE_PORT` from (default: `127.0.0.1` - the SSH server itself, but could be any accessible port from other host from the same network as the SSH server)
- `LOCAL_PORT`: the remote port will be exposed on this port on the local host -container- (default: the same as `REMOTE_PORT`)
- `LOCAL_HOST`: where to bind the `LOCAL_PORT` - this can be used to limit access to the port (default: `0.0.0.0` - any host, and since this will be running on a container, it can be limited using Docker port mapping)

Mapping examples:

- `80`: forward port 80 from remote host (where SSH server is running) to port 80 of local container
- `192.168.0.200:80`: forward port 80 from the host 192.168.0.200 (visible by the SSH server) to port 80 of local container
- `8080:127.0.0.1:80`: forward port 80 from remote host (where SSH server is running) to port 8080 of local container
- `127.0.0.1:80:127.0.0.1:80`: forward port 80 from remote host (where SSH server is running) to port 80 of local container, and only accesible by the container itself (or by the host, if network=host)

Multiple mappings can be defined by:

- Using a single `MAPPINGS` env var, and splitting them by `;` (when running docker run, the value must be passed between quotes, like `-e MAPPINGS="8080:127.0.0.1:80; 4443:127.0.0.1:443"`). Spaces are ignored.
- Using multiple environment variables, starting with `MAPPING`. For example, they could be named like "MAPPING1", "MAPPING_1", "MAPPING_SSH", and so on. Inside each env var, one or many mappings can be defined. All of them will be merged and used.

#### Reverse port forwarding

Any mapping that starts with a `R` is considered a reverse port forward. This allows to map a port on the client network to the remote server network.

By defining the following setting: `-e MAPPINGS="R8080:127.0.0.1:80"`, the port 80 on the client host will be accessible on the port 8080 on the remote SSH server host.
Notice that you might have to set container network to `host` in order to forward host ports.

Reverse and non-reverse mappings can be combined on the same connection, thus, the same container.

### SSH server settings

- `SSH_HOST`: remote host/IP to connect to (required)
- `SSH_PORT`: SSH port on the remote host (default: `22`)
- `SSH_USER`: user to connect with on the remote SSH server (required)

### Other settings

- `SSH_COMPRESSION`: set to 1 to enable SSH Compression (default: `0`)
- `SSH_IPV6`: set to `1` to connect using IPv6 (default: `0` - use IPv4)
- `SSH_KEY_LOCATION`: where to read SSH key from, inside container (default: `/ssh_key`)
- `SSH_KEY_WRITE_LOCATION`: the SSH key read from `SSH_KEY_LOCATION` is copied to this path, to ensure the file permissions are correct
- You can define [autossh Environment settings](https://linux.die.net/man/1/autossh) on the container and they will be used (example: `AUTOSSH_DEBUG` set to `1` to enable verbose debug output for autossh)

## TODO

- Allow SSH keys with password
- Allow login with password only (no key)
- Define mappings & settings through file
- Update mappings in real time, avoiding downtime
- Allow proxy tunnel
- Allow to set autossh reconnection settings
- Allow to set custom SSH options (for unsupported settings)
- Allow to provide SSH server public key for host verification
- Add healthcheck based on forwarded ports
- Add automated tests
- Add sshd_config server settings examples
