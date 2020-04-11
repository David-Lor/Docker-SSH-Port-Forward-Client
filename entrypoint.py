#!/usr/bin/env python

import os
import subprocess
import contextlib
from typing import List, Optional


class Mapping:
    def __init__(self, remote_port, local_port=None, remote_host=None, local_host=None):
        self.remote_port = remote_port
        self.local_port = local_port if local_port else self.remote_port
        self.remote_host = remote_host if remote_host else "127.0.0.1"
        self.local_host = local_host if local_host else "0.0.0.0"

    def to_command(self) -> List[str]:
        mapping_chunks = [self.local_host, self.local_port, self.remote_host, self.remote_port]
        return ["-L", ":".join(mapping_chunks)]


class Settings:
    def __init__(self):
        raw_mappings = self.getenv("MAPPINGS")
        self.mappings = self.parse_mappings(raw_mappings)
        self.user = self.getenv("SSH_USER")
        self.host = self.getenv("SSH_HOST")
        self.port = self.getenv("SSH_PORT")
        self.read_ssh_key_location = self.getenv("SSH_KEY_LOCATION")
        self.write_ssh_key_location = self.getenv("SSH_KEY_WRITE_LOCATION")
        self.ipv6 = int(self.getenv("SSH_IPV6"))
        self.compression = int(self.getenv("SSH_COMPRESSION"))

    @staticmethod
    def getenv(key, default_value=None, allow_empty=False) -> Optional[str]:
        value = os.getenv(key, default_value)
        if value is None or (value == "" and not allow_empty):
            print(f"The environment variable {key} is not set!")
            exit(1)
        return value

    @staticmethod
    def parse_mappings(raw_mappings) -> List[Mapping]:
        raw_mapping_chunks = raw_mappings.split(";")
        if not raw_mapping_chunks:
            print("No port mappings defined!")
            exit(0)

        mappings = list()
        for chunk in raw_mapping_chunks:
            sub_chunks = chunk.strip().split(":")
            if not sub_chunks:
                continue

            kwargs = dict()
            with contextlib.suppress(IndexError):
                kwargs["remote_port"] = sub_chunks.pop()
                kwargs["remote_host"] = sub_chunks.pop()
                kwargs["local_port"] = sub_chunks.pop()
                kwargs["local_host"] = sub_chunks.pop()

            mappings.append(Mapping(**kwargs))

        return mappings

    def mappings_to_command(self) -> List[str]:
        command_mappings = list()
        for mapping in self.mappings:
            command_mappings.extend(mapping.to_command())
        return command_mappings

    def login_to_command(self) -> str:
        return f"{self.user}@{self.host}"

    def ipv_to_command(self) -> str:
        return "-6" if self.ipv6 else "-4"

    def compression_to_command(self) -> List[str]:
        return ["-C"] if self.compression else []


def setup_ssh_key(settings: Settings):
    if not os.path.exists(settings.write_ssh_key_location):
        print("Copying SSH key...")
        subprocess.call(["cp", settings.read_ssh_key_location, settings.write_ssh_key_location])
        subprocess.call(["chmod", "600", settings.write_ssh_key_location])


def run_ssh(settings: Settings):
    command = [
        "autossh", "-N", *settings.mappings_to_command(),
        "-i", settings.write_ssh_key_location,
        "-o", "StrictHostKeyChecking=no",
        "-p", settings.port, settings.ipv_to_command(),
        *settings.compression_to_command(),
        settings.login_to_command()
    ]

    print(f"Running {' '.join(command)} ...")
    result = subprocess.call(command)

    print(f"SSH client process ended with exit code {result}")
    exit(result)


def main():
    try:
        settings = Settings()
        setup_ssh_key(settings)
        run_ssh(settings)
    except (KeyboardInterrupt, InterruptedError):
        print("Execution interrupted")


if __name__ == '__main__':
    main()
