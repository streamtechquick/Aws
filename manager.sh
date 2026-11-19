#!/usr/bin/env bash
set -Eeuo pipefail
cd "$(dirname "$0")"
if [ ! -x .venv/bin/python ]; then
  python3 -m venv .venv
  .venv/bin/pip install -r requirements.txt
fi
echo "ARABI VPS Manager"
echo "1) Host status"
echo "2) List VMs"
echo "3) Start API server"
echo "4) Start Discord bot"
echo "5) Exit"
read -r -p "Choose: " choice
case "$choice" in
  1) .venv/bin/python -c 'import core; print(core.host_info())' ;;
  2) .venv/bin/python -c 'import core; print(core.list_vms())' ;;
  3) .venv/bin/uvicorn api:app --host 0.0.0.0 --port 6969 ;;
  4) .venv/bin/python bot/main.py ;;
  5) exit 0 ;;
  *) echo "Invalid option"; exit 1 ;;
esac
