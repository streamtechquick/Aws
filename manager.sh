#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"

header() {
  clear 2>/dev/null || true
  echo "================================"
  echo "       ARABI VPS MANAGER"
  echo "================================"
  echo
}

status() {
  echo "HOST: $(hostname)"
  echo "OS: $(uname -s)"
  echo "CPU: $(nproc 2>/dev/null || echo unknown)"
  echo
  free -h 2>/dev/null || true
  echo
  df -h "$ROOT"
  echo
  if [ -e /dev/kvm ]; then
    echo "KVM: AVAILABLE"
  else
    echo "KVM: NOT AVAILABLE"
    echo "VM provisioning is disabled on this host."
  fi
}

list_vms() {
  echo "===== CONFIGURED INSTANCES ====="
  find "$ROOT/instances" -mindepth 1 -maxdepth 1 -type d \
    -printf '%f\n' 2>/dev/null || true
}

while true; do
  header
  echo "1. Host status"
  echo "2. List instances"
  echo "3. Check KVM capability"
  echo "4. Exit"
  echo
  read -r -p "Select: " choice
  case "$choice" in
    1) status ;;
    2) list_vms ;;
    3)
      if [ -e /dev/kvm ]; then
        echo "KVM device detected."
      else
        echo "KVM unavailable. No VM will be created."
      fi
      ;;
    4) exit 0 ;;
    *) echo "Invalid option." ;;
  esac
  echo
  read -r -p "Press Enter..." _
done
