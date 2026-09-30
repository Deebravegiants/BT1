# [M] ice: fix NULL pointer dereference in ice_unplug_aux_dev() on reset

## Summary
Severity: Medium
Advisory: CVE-2025-39814
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-16
Source: https://osv.dev/vulnerability/CVE-2025-39814
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.16.0 <6.16.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

ice: fix NULL pointer dereference in ice_unplug_aux_dev() on reset

Issuing a reset when the driver is loaded without RDMA support, will
results in a crash as it attempts to remove RDMA's non-existent auxbus
device:
echo 1 > /sys/class/net/<if>/device/reset

BUG: kernel NULL pointer dereference, address: 0000000000000008
...
RIP: 0010:ice_unplug_aux_dev+0x29/0x70 [ice]
...
Call Trace:
<TASK>
ice_prepare_for_reset+0x77/0x260 [ice]
pci_dev_save_and_disable+0x2c/0x70
pci_reset_function+0x88/0x130
reset_store+0x5a/0xa0
kernfs_fop_write_iter+0x15e/0x210
vfs_write+0x273/0x520
ksys_write+0x6b/0xe0
do_syscall_64+0x79/0x3b0
entry_SYSCALL_64_after_hwframe+0x76/0x7e

ice_unplug_aux_dev() checks pf->cdev_info->adev for NULL pointer, but
pf->cdev_info will also be NULL, leading to the deref in the trace above.

Introduce a flag to be set when the creation of the auxbus device is
successful, to avoid multiple NULL pointer checks in ice_unplug_aux_dev().

## References
- https://git.kernel.org/stable/c/60dfe2434eed13082f26eb7409665dfafb38fa51
- https://git.kernel.org/stable/c/db783756a7d7cfaea039411971d0dc0a374e85cb
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39814.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39814
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
