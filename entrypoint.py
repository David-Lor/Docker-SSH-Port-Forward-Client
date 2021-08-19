#!/usr/bin/env python

import os
import subprocess
import contextlib
from typing import List, Optional


class Mapping:
    def __init__(self, remote_port, local_port=None, remote_host=None, local_host=None, reverse=False):
        self.remote_port = remote_port
        self.local_port = local_port if local_port else self.remote_port
        self.remote_host = remote_host if remote_host else "127.0.0.1"
        self.local_host = local_host if local_host else "0.0.0.0"
        self.reverse = reverse

    def to_command(self) -> List[str]:
        mapping_chunks = [self.local_host, self.local_port, self.remote_host, self.remote_port]
        beginning = "-L" if not self.reverse else "-R"
        return [beginning, ":".join(mapping_chunks)]


class SettingsConst:
    mapping_prefix = "MAPPING"
    mapping_split_char = ";"
    ssh_user = "SSH_USER"
    ssh_host = "SSH_HOST"
    ssh_port = "SSH_PORT"
    ssh_key_location_read = "SSH_KEY_LOCATION"
    ssh_key_location_write = "SSH_KEY_WRITE_LOCATION"
    ssh_ipv6 = "SSH_IPV6"
    ssh_compression = "SSH_COMPRESSION"


class Settings:
    def __init__(self):
        raw_mappings_chunks = self.load_mappings()
        self.mappings = self.parse_mappings(raw_mappings_chunks)
        if not self.mappings:
            print("No port mappings defined or none of them are valid")
            exit(1)

        self.user = self.getenv(SettingsConst.ssh_user)
        self.host = self.getenv(SettingsConst.ssh_host)
        self.port = self.getenv(SettingsConst.ssh_port)
        self.read_ssh_key_location = self.getenv(SettingsConst.ssh_key_location_read)
        self.write_ssh_key_location = self.getenv(SettingsConst.ssh_key_location_write)
        self.ipv6 = int(self.getenv(SettingsConst.ssh_ipv6))
        self.compression = int(self.getenv(SettingsConst.ssh_compression))

    @staticmethod
    def getenv(key, default_value=None, allow_empty=False) -> Optional[str]:
        value = os.getenv(key, default_value)
        if value is None or (value == "" and not allow_empty):
            print(f"The environment variable {key} is not set!")
            exit(1)
        return value

    @staticmethod
    def load_mappings() -> List[str]:
        """Load all the environment variables used for port mappings. Return the raw mappings chunks, corresponding
        to each mapping parsed from all the environment variables available."""
        raw_mappings_chunks = list()
        for key, value in os.environ.items():
            if key.startswith(SettingsConst.mapping_prefix):
                value_mappings_chunks = [v.strip() for v in value.split(SettingsConst.mapping_split_char) if v]
                raw_mappings_chunks.extend(value_mappings_chunks)

        return raw_mappings_chunks

    @staticmethod
    def parse_mappings(raw_mappings_chunks: List[str]) -> List[Mapping]:
        """Given raw mapping chunks, parse them and return Mapping objects. Invalid mappings are ignored."""
        mappings = list()

        for chunk in raw_mappings_chunks:
            kwargs = dict()

            if chunk.startswith("R"):
                kwargs["reverse"] = True
                chunk = chunk[1:]

            sub_chunks = chunk.strip().split(":")
            if not sub_chunks:
                continue

            with contextlib.suppress(IndexError):
                kwargs["remote_port"] = sub_chunks.pop()
                kwargs["remote_host"] = sub_chunks.pop()
                kwargs["local_port"] = sub_chunks.pop()
                kwargs["local_host"] = sub_chunks.pop()

            mapping = Mapping(**kwargs)
            print("Parsed port mapping:", mapping.__dict__)
            mappings.append(mapping)

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
