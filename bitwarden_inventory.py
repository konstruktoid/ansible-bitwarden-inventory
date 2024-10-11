#!/usr/bin/env python
# ruff: noqa: T201
"""Populate a Ansible inventory with information from Bitwarden."""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

import yaml

DOCUMENTATION = """
    name: bitwarden_inventory
    author:
      - Thomas Sjögren (@konstruktoid)
    short_description: Populate a Ansible inventory with information from Bitwarden.
    description:
      - Populates a Ansible inventory with information from Bitwarden.
      - Uses a YAML configuration file bitwarden_inventory.yml.
"""

EXAMPLES = """
# bitwarden_inventory.yml configuration file:
---
bitwarden_hosts:
  test-server-01: "1c7adc62-471d-494f-bf0d-af7e00f99c64"
  test-server-02:
  webserver: "test-server-01"
...
"""

try:
    import json
except ImportError:
    import simplejson as json

__version__ = "0.0.1"


class AnsibleBitwardenInventory:
    """The AnsibleBitwardenInventory class."""

    def __init__(self) -> None:
        """Initialize the class."""
        self.bitwarden_cmd = shutil.which("bw")
        self.inventory = {}
        self.inventory_content = {}
        self.generated_inventory = {}
        self.read_cli_args()
        self.ensure_bitwarden()
        self.generate_inventory()

    def generate_inventory(self) -> None:
        """Generate the inventory."""
        try:
            cwd = Path.cwd()
            self.configuration_file = f"{cwd}/bitwarden_inventory.yml"

            if not Path(self.configuration_file).is_file():
                print(self.configuration_file + " can't be found.")
                sys.exit(1)
            else:
                with Path.open(
                    "./bitwarden_inventory.yml",
                    encoding="utf-8",
                ) as inventory_file:
                    self.inventory = yaml.safe_load(inventory_file)

            self.generated_inventory = self.inventory_content
            self.inventory_content["bitwarden_hosts"] = []
            self.inventory_content["_meta"] = {}
            self.inventory_content["_meta"]["hostvars"] = {}

            for inventory in self.inventory.values():
                for name, identifier in inventory.items():
                    if not identifier:
                        identifier = name  # noqa: PLW2901

                    host_bw_json = json.loads(
                        subprocess.run(  # noqa: S603
                            [self.bitwarden_cmd, "get", "item", identifier],
                            shell=False,
                            text=True,
                            capture_output=True,
                            check=False,
                        ).stdout,
                    )

                    self.inventory_content["bitwarden_hosts"].append(name)
                    self.inventory_content["_meta"]["hostvars"][name] = {}
                    ansible_host = urlparse(
                        host_bw_json["login"]["uris"][0]["uri"],
                    ).netloc
                    ansible_user = host_bw_json["login"]["username"]
                    ansible_password = host_bw_json["login"]["password"]

                    if ansible_host:
                        self.inventory_content["_meta"]["hostvars"][name][
                            "ansible_host"
                        ] = ansible_host
                    if ansible_user:
                        self.inventory_content["_meta"]["hostvars"][name][
                            "ansible_user"
                        ] = ansible_user
                    if ansible_password:
                        self.inventory_content["_meta"]["hostvars"][name][
                            "ansible_password"
                        ] = ansible_password
                        self.inventory_content["_meta"]["hostvars"][name][
                            "ansible_become_password"
                        ] = ansible_password

        except subprocess.CalledProcessError as exception:
            print("There was an issue with:\n  " + name + ": " + identifier)
            print(exception)
            sys.exit(1)

        if self.args.list:
            print(json.dumps(self.generated_inventory, sort_keys=True, indent=2))
        else:
            print(json.dumps(self.generated_inventory, sort_keys=True))

    def ensure_bitwarden(self) -> None:
        """Ensure Bitwarden is installed and the user is logged in."""
        try:
            if not self.bitwarden_cmd:
                print("bw doesn't seem to be installed. Exiting.")
                sys.exit(1)

            if not subprocess.check_output(  # noqa: S603
                [self.bitwarden_cmd, "list", "items"],
                shell=False,
            ):
                sys.exit(1)

        except Exception as exception_string:  # noqa: BLE001
            print("Exception: ", str(exception_string), file=sys.stderr)
            sys.exit(1)

    def list_bitwarden_vault(self) -> None:
        """Test the bw ls function."""
        try:
            subprocess.run(  # noqa: S603
                [self.bitwarden_cmd, "list", "items"],
                shell=False,
                check=False,
            )

        except Exception as exception_string:  # noqa: BLE001
            print("Exception: ", str(exception_string), file=sys.stderr)
            sys.exit(1)

    def read_cli_args(self) -> None:
        """Command line arguments and help information."""
        parser = argparse.ArgumentParser(
            description="Populate a Ansible inventory with information from Bitwarden.",
            epilog="version: " + __version__,
        )
        parser.add_argument(
            "-l",
            "--list",
            help="print the inventory",
            action="store_true",
        )

        self.args = parser.parse_args()


AnsibleBitwardenInventory()
