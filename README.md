# Dynamic Bitwarden Ansible Inventory

Requires a [Bitwarden](https://www.bitwarden.com/) account and the [bw](https://bitwarden.com/help/cli/)
CLI client.

The `bitwarden_inventory.py` script uses the `bitwarden_inventory.yml`
configuration file to fetch the named servers from the current logged in
Bitwarden account using `bw`, and then generate an [Ansible](https://www.ansible.com/)
inventory.

## Examples and Usage

The `bitwarden_inventory.yml` configuration file names and fetches the hosts
using `name: identifier`, where the `name` variable is what the host will be
named in the inventory and the `identifier` is used to identify the host in
Bitwarden.

Both the name and the ID number from e.g. `bw list items` can be used as an
identifier for a host.

If the ID is omitted, the name will be used as the identifier.

Note that the script will fail if the name or ID is incorrect or missing.

The Bitwarden `user` and `password` fields will be used to populate
`ansible_user`, `ansible_password` and `ansible_become_password`.
The `ansible_host` address is the extracted netloc from the Bitwarden `uri` field
using [urllib.parse.urlparse](https://docs.python.org/3/library/urllib.parse.html).

Example `bw --pretty list items --search test-server` output:

```json
[
  {
    "object": "item",
    "id": "1c7adc62-471d-494f-bf0d-af7e00f99c64",
    "organizationId": null,
    "folderId": null,
    "type": 1,
    "reprompt": 0,
    "name": "test-server-01",
    "notes": null,
    "favorite": false,
    "login": {
      "uris": [
        {
          "match": null,
          "uri": "192.168.0.191"
        }
      ],
      "username": "testadmin01",
      "password": "testadminpassword01",
      "totp": null,
      "passwordRevisionDate": "2023-01-02T15:37:01.634Z"
    },
    "collectionIds": [],
    "revisionDate": "2023-01-02T15:37:32.600Z",
    "deletedDate": null,
    "passwordHistory": [
      {
        "lastUsedDate": "2023-01-02T15:37:01.634Z",
        "password": "testadmin01"
      }
    ]
  },
  {
    "object": "item",
    "id": "e5a9a311-27bc-475d-9098-af7e00f9ae50",
    "organizationId": null,
    "folderId": null,
    "type": 1,
    "reprompt": 0,
    "name": "test-server-02",
    "notes": null,
    "favorite": false,
    "login": {
      "uris": [
        {
          "match": null,
          "uri": "192.168.0.192"
        }
      ],
      "username": "testadmin02",
      "password": "testadminpassword02",
      "totp": null,
      "passwordRevisionDate": "2023-01-02T15:37:22.916Z"
    },
    "collectionIds": [],
    "revisionDate": "2023-01-02T15:37:23.156Z",
    "deletedDate": null,
    "passwordHistory": [
      {
        "lastUsedDate": "2023-01-02T15:37:22.916Z",
        "password": "testadmin02"
      }
    ]
  }
]
```

Configuration file based on the above:

```yaml
---
bitwarden_hosts:
  test-server-01: "1c7adc62-471d-494f-bf0d-af7e00f99c64"
  test-server-02:
  webserver: "test-server-01"
...
```

Running `ansible-inventory -i bitwarden_inventory.py --list --yaml` will then
generate the following inventory:

```yaml
all:
  children:
    bitwarden_hosts:
      hosts:
        test-server-01:
          ansible_become_password: testadminpassword01
          ansible_password: testadminpassword01
          ansible_user: testadmin01
        test-server-02:
          ansible_become_password: testadminpassword02
          ansible_password: testadminpassword02
          ansible_user: testadmin02
        webserver:
          ansible_become_password: testadminpassword01
          ansible_password: testadminpassword01
          ansible_user: testadmin01
    ungrouped: {}
```
