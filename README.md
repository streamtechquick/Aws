# ARABI VPS Manager v2.0.0

ARABI VPS Manager control plane and Discord bot.

## Requirements
- Ubuntu/Debian Linux host
- KVM available at `/dev/kvm`
- libvirt, `virsh`, `virt-install`
- Python 3.10+

## Host setup
Install system packages:
`sudo apt install qemu-kvm libvirt-daemon-system libvirt-clients virtinst python3-venv`

Copy `.env.example` to `.env` and set a long random `API_KEY`.
Set `DISCORD_BOT_TOKEN` and `DISCORD_ADMIN_IDS` (comma-separated Discord user IDs).

Install Python packages:
`python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`

Run manager:
`./manager.sh`

Run API directly:
`.venv/bin/uvicorn api:app --host 0.0.0.0 --port 6969`

Run Discord bot:
`.venv/bin/python bot/main.py`

## VM creation
The ISO path must exist on the KVM host. VM creation uses libvirt's default
network and creates a qcow2 disk. Check the network and storage configuration
before exposing this service.

## Safety
- API endpoints require `X-API-Key`.
- VM delete removes the libvirt definition only; disk storage is preserved.
- `force_stop` is not exposed as a Discord command.
- Codespaces are development environments and are not KVM VPS hosts.
