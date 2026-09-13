# [H] vfio/pci: Properly hide first-in-list PCIe extended capability

## Summary
Severity: High
Advisory: CVE-2024-53214
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-53214
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.6.0 <4.19.325, >=4.20.0 <5.4.287, >=5.5.0 <5.10.231, >=5.11.0 <5.15.174, >=5.16.0 <6.1.120, >=6.2.0 <6.6.64, >=6.7.0 <6.11.11, >=6.12.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

vfio/pci: Properly hide first-in-list PCIe extended capability

There are cases where a PCIe extended capability should be hidden from
the user. For example, an unknown capability (i.e., capability with ID
greater than PCI_EXT_CAP_ID_MAX) or a capability that is intentionally
chosen to be hidden from the user.

Hiding a capability is done by virtualizing and modifying the 'Next
Capability Offset' field of the previous capability so it points to the
capability after the one that should be hidden.

The special case where the first capability in the list should be hidden
is handled differently because there is no previous capability that can
be modified. In this case, the capability ID and version are zeroed
while leaving the next pointer intact. This hides the capability and
leaves an anchor for the rest of the capability list.

However, today, hiding the first capability in the list is not done
properly if the capability is unknown, as struct
vfio_pci_core_device->pci_config_map is set to the capability ID during
initialization but the capability ID is not properly checked later when
used in vfio_config_do_rw(). This leads to the following warning [1] and
to an out-of-bounds access to ecap_perms array.

Fix it by checking cap_id in vfio_config_do_rw(), and if it is greater
than PCI_EXT_CAP_ID_MAX, use an alternative struct perm_bits for direct
read only access instead of the ecap_perms array.

Note that this is safe since the above is the only case where cap_id can
exceed PCI_EXT_CAP_ID_MAX (except for the special capabilities, which
are already checked before).

[1]

WARNING: CPU: 118 PID: 5329 at drivers/vfio/pci/vfio_pci_config.c:1900 vfio_pci_config_rw+0x395/0x430 [vfio_pci_core]
CPU: 118 UID: 0 PID: 5329 Comm: simx-qemu-syste Not tainted 6.12.0+ #1
(snip)
Call Trace:
 <TASK>
 ? show_regs+0x69/0x80
 ? __warn+0x8d/0x140
 ? vfio_pci_config_rw+0x395/0x430 [vfio_pci_core]
 ? report_bug+0x18f/0x1a0
 ? handle_bug+0x63/0xa0
 ? exc_invalid_op+0x19/0x70
 ? asm_exc_invalid_op+0x1b/0x20
 ? vfio_pci_config_rw+0x395/0x430 [vfio_pci_core]
 ? vfio_pci_config_rw+0x244/0x430 [vfio_pci_core]
 vfio_pci_rw+0x101/0x1b0 [vfio_pci_core]
 vfio_pci_core_read+0x1d/0x30 [vfio_pci_core]
 vfio_device_fops_read+0x27/0x40 [vfio]
 vfs_read+0xbd/0x340
 ? vfio_device_fops_unl_ioctl+0xbb/0x740 [vfio]
 ? __rseq_handle_notify_resume+0xa4/0x4b0
 __x64_sys_pread64+0x96/0xc0
 x64_sys_call+0x1c3d/0x20d0
 do_syscall_64+0x4d/0x120
 entry_SYSCALL_64_after_hwframe+0x76/0x7e

## References
- https://git.kernel.org/stable/c/06f2fcf49854ad05a09d09e0dbee6544fff04695
- https://git.kernel.org/stable/c/0918f5643fc6c3f7801f4a22397d2cc09ba99207
- https://git.kernel.org/stable/c/1ef195178fb552478eb2587df4ad3be14ef76507
- https://git.kernel.org/stable/c/4464e5aa3aa4574063640f1082f7d7e323af8eb4
- https://git.kernel.org/stable/c/6c6502d944168cbd7e03a4a08ad6488f78d73485
- https://git.kernel.org/stable/c/7d121f66b67921fb3b95e0ea9856bfba53733e91
- https://git.kernel.org/stable/c/949bee8065a85a5c6607c624dc05b5bc17119699
- https://git.kernel.org/stable/c/9567bd34aa3b986736c290c5bcba47e0182ac47a
- https://git.kernel.org/stable/c/fe4bf8d0b6716a423b16495d55b35d3fe515905d
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53214.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53214
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
