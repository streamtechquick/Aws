import os
import re
import shutil
import subprocess
from pathlib import Path

LIBVIRT_URI = os.getenv("LIBVIRT_URI", "qemu:///system")
VM_STORAGE = Path(os.getenv("VM_STORAGE", "/var/lib/libvirt/images"))
DEFAULT_NETWORK = os.getenv("DEFAULT_NETWORK", "default")

def run(args, timeout=120):
    p = subprocess.run(
        args, text=True, capture_output=True, timeout=timeout
    )
    if p.returncode:
        raise RuntimeError((p.stderr or p.stdout or "Command failed").strip())
    return p.stdout.strip()

def require_host():
    if not Path("/dev/kvm").exists():
        raise RuntimeError("KVM unavailable: /dev/kvm was not found.")
    if not shutil.which("virsh") or not shutil.which("virt-install"):
        raise RuntimeError("Install libvirt-clients and virtinst first.")

def valid_name(name):
    if not re.fullmatch(r"[a-zA-Z][a-zA-Z0-9_-]{1,30}", name):
        raise ValueError("Invalid VM name. Use 2-31 letters, digits, _ or -.")
    return name

def host_info():
    import psutil
    return {
        "hostname": __import__("socket").gethostname(),
        "cpu_cores": psutil.cpu_count(logical=True),
        "ram_total_mb": round(psutil.virtual_memory().total / 1048576),
        "ram_available_mb": round(psutil.virtual_memory().available / 1048576),
        "disk_total_gb": round(psutil.disk_usage("/").total / 1073741824, 2),
        "disk_free_gb": round(psutil.disk_usage("/").free / 1073741824, 2),
        "kvm": Path("/dev/kvm").exists(),
        "libvirt": bool(shutil.which("virsh")),
    }

def list_vms():
    require_host()
    names = run(["virsh", "-c", LIBVIRT_URI, "list", "--all", "--name"]).splitlines()
    result = []
    for name in filter(None, names):
        try:
            state = run(["virsh", "-c", LIBVIRT_URI, "domstate", name])
        except Exception:
            state = "unknown"
        result.append({"name": name, "state": state})
    return result

def create_vm(name, ram_mb, vcpus, disk_gb, iso):
    require_host()
    name = valid_name(name)
    if not (512 <= int(ram_mb) <= 262144):
        raise ValueError("RAM must be between 512 and 262144 MB.")
    if not (1 <= int(vcpus) <= 64):
        raise ValueError("CPU must be between 1 and 64.")
    if not (5 <= int(disk_gb) <= 2048):
        raise ValueError("Disk must be between 5 and 2048 GB.")

    iso_path = Path(iso).resolve()
    if not iso_path.is_file() or iso_path.suffix.lower() != ".iso":
        raise ValueError("Provide an existing .iso file on the KVM host.")

    if any(x["name"] == name for x in list_vms()):
        raise ValueError("A VM with this name already exists.")

    VM_STORAGE.mkdir(parents=True, exist_ok=True)
    disk = VM_STORAGE / f"{name}.qcow2"
    if disk.exists():
        raise ValueError("Disk file already exists; refusing to overwrite it.")

    run([
        "virt-install", "--connect", LIBVIRT_URI,
        "--name", name,
        "--memory", str(int(ram_mb)),
        "--vcpus", str(int(vcpus)),
        "--disk", f"path={disk},size={int(disk_gb)},format=qcow2",
        "--cdrom", str(iso_path),
        "--network", f"network={DEFAULT_NETWORK}",
        "--graphics", "none",
        "--noautoconsole",
    ], timeout=180)
    return {"name": name, "disk": str(disk), "status": "created"}

def vm_action(name, action):
    require_host()
    name = valid_name(name)
    commands = {
        "start": "start",
        "stop": "shutdown",
        "force_stop": "destroy",
        "restart": "reboot",
    }
    if action not in commands:
        raise ValueError("Unsupported action.")
    return run(["virsh", "-c", LIBVIRT_URI, commands[action], name])

def delete_vm(name):
    require_host()
    name = valid_name(name)
    # Undefine only. Storage is deliberately preserved.
    return run(["virsh", "-c", LIBVIRT_URI, "undefine", name])
