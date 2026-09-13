# [H] iommu/vt-d: Fix RB-tree corruption in probe error path

## Summary
Severity: High
Advisory: CVE-2026-74355
Ecosystem: Linux
CVSS: 8.2 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74355
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.15.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

iommu/vt-d: Fix RB-tree corruption in probe error path

The info->node RB-tree member is zero-initialized via kzalloc. If
a device does not support ATS, the device_rbtree_insert() call is
skipped. If a subsequent probe step fails, the error path jumps to
device_rbtree_remove(), which misinterprets the zeroed node as
a tree root and corrupts the device RB-tree.

Fix this by explicitly initializing the RB-node as empty using
RB_CLEAR_NODE() during initialization and guarding the removal with
RB_EMPTY_NODE().

## References
- https://git.kernel.org/stable/c/43bd9e6d5513cb1edbafdeef146a1edc3aaced56
- https://git.kernel.org/stable/c/d16923a45d4d08367650fdc3451c89299ab6ac5a
- https://git.kernel.org/stable/c/f5102e0fc3c6dc8685549891a96e4589fdb3e211
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74355.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74355
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
