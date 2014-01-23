"""
Network introspection utilities using ioctl and the /proc filesystem.
"""
import os

from landscape.lib.fs import read_file


def get_vm_info(root_path="/"):
    """
    Return a string with the virtualization type if it's known, an empty string
    otherwise.

    It loops through some possible configurations and return a string with
    the name of the technology being used or None if there's no match
    """
    def join_root_path(path):
        return os.path.join(root_path, path)

    xen_paths = ["proc/sys/xen", "proc/xen"]
    xen_paths = map(join_root_path, xen_paths)
    vz_path = join_root_path("proc/vz")

    if os.path.exists(vz_path):
        return "openvz"
    elif filter(os.path.exists, xen_paths):
        return "xen"

    # /sys/bus/xen exists on most machines, but only virtual machines have
    # devices
    sys_xen_path = join_root_path("sys/bus/xen/devices")
    if os.path.isdir(sys_xen_path) and os.listdir(sys_xen_path):
        return "xen"

    sys_vendor_path = join_root_path("sys/class/dmi/id/sys_vendor")
    if not os.path.exists(sys_vendor_path):
        # Some virtualised CPU architectures indicate this via cpuinfo
        cpuinfo_path = join_root_path("proc/cpuinfo")
        if os.path.exists(cpuinfo_path):
            cpuinfo = read_file(cpuinfo_path)
            if "(emulated by qemu)" in cpuinfo:
                return "kvm"
        return ""

    vendor = read_file(sys_vendor_path)
    content_vendors_map = (
        ("VMware, Inc.", "vmware"),
        ("Microsoft Corporation", "hyperv"),
        ("Bochs", "kvm"),
        ("OpenStack", "kvm"),
        ("innotek GmbH", "virtualbox"))
    for name, vm_type in content_vendors_map:
        if name in vendor:
            return vm_type

    return ""


def get_container_info(path="/run/container_type"):
    """
    Return a string with the type of container the client is running in, if
    any, an empty string otherwise.
    """
    return read_file(path).strip() if os.path.exists(path) else ""
