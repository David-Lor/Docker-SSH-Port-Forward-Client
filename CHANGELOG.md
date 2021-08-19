# Changelog

# dev

- Change base image to Alpine
- Default AutoSSH Monitoring Port setting to disabled (requires being specified in alpine autossh)
- Allow choosing between AutoSSH or vanilla SSH client
- Add multiarch support (linux/amd64, linux/arm/v7)
- Allow defining port mappings using multiple environment variables (starting with the "MAPPING" prefix)

# 0.3.1

- Use root user in container to avoid problems with SSH key read permissions or mapping on privileged ports

# 0.2.1

- Allow defining reverse port forwarding mappings

# 0.0.1

- Add setting to enable compression

# 0.0.1

- Initial release
