# [M] CVE-2021-47005

## Summary
Severity: Medium
Advisory: CVE-2021-47005
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-28
Source: https://osv.dev/vulnerability/CVE-2021-47005
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

PCI: endpoint: Fix NULL pointer dereference for ->get_features()

get_features ops of pci_epc_ops may return NULL, causing NULL pointer
dereference in pci_epf_test_alloc_space function. Let us add a check for
pci_epc_feature pointer in pci_epf_test_bind before we access it to avoid
any such NULL pointer dereference and return -ENOTSUPP in case
pci_epc_feature is not found.

When the patch is not applied and EPC features is not implemented in the
platform driver, we see the following dump due to kernel NULL pointer
dereference.

Call trace:
 pci_epf_test_bind+0xf4/0x388
 pci_epf_bind+0x3c/0x80
 pci_epc_epf_link+0xa8/0xcc
 configfs_symlink+0x1a4/0x48c
 vfs_symlink+0x104/0x184
 do_symlinkat+0x80/0xd4
 __arm64_sys_symlinkat+0x1c/0x24
 el0_svc_common.constprop.3+0xb8/0x170
 el0_svc_handler+0x70/0x88
 el0_svc+0x8/0x640
Code: d2800581 b9403ab9 f9404ebb 8b394f60 (f9400400)
---[ end trace a438e3c5a24f9df0 ]---

## References
- https://git.kernel.org/stable/c/6613bc2301ba291a1c5a90e1dc24cf3edf223c03
- https://git.kernel.org/stable/c/679ebad058b8168f10e63876d63b0877fd2fe784
- https://git.kernel.org/stable/c/bbed83d7060e07a5d309104d25a00f0a24441428
- https://git.kernel.org/stable/c/0169d4f0bee44fdfef908c13ed21fcb326c38695
