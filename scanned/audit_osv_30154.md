# [M] PCI: Hold rescan lock while adding devices during host probe

## Summary
Severity: Medium
Advisory: CVE-2024-50122
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-05
Source: https://osv.dev/vulnerability/CVE-2024-50122
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.11.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

PCI: Hold rescan lock while adding devices during host probe

Since adding the PCI power control code, we may end up with a race between
the pwrctl platform device rescanning the bus and host controller probe
functions. The latter need to take the rescan lock when adding devices or
we may end up in an undefined state having two incompletely added devices
and hit the following crash when trying to remove the device over sysfs:

  Unable to handle kernel NULL pointer dereference at virtual address 0000000000000000
  Internal error: Oops: 0000000096000004 [#1] SMP
  Call trace:
    __pi_strlen+0x14/0x150
    kernfs_find_ns+0x80/0x13c
    kernfs_remove_by_name_ns+0x54/0xf0
    sysfs_remove_bin_file+0x24/0x34
    pci_remove_resource_files+0x3c/0x84
    pci_remove_sysfs_dev_files+0x28/0x38
    pci_stop_bus_device+0x8c/0xd8
    pci_stop_bus_device+0x40/0xd8
    pci_stop_and_remove_bus_device_locked+0x28/0x48
    remove_store+0x70/0xb0
    dev_attr_store+0x20/0x38
    sysfs_kf_write+0x58/0x78
    kernfs_fop_write_iter+0xe8/0x184
    vfs_write+0x2dc/0x308
    ksys_write+0x7c/0xec

## References
- https://git.kernel.org/stable/c/1d59d474e1cb7d4fdf87dfaf96f44647f13ea590
- https://git.kernel.org/stable/c/d4f38a0e7cc94615f63cf7765ca117e5cc2773ae
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50122.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50122
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
