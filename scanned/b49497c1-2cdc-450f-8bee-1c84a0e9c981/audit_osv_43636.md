# [H] Bluetooth: mgmt: fix pending command UAF in EIR updates

## Summary
Severity: High
Advisory: CVE-2026-74511
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74511
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.6.151, >=6.7.0 <6.12.103, >=6.13.0 <6.18.44, >=6.16.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: mgmt: fix pending command UAF in EIR updates

MGMT_OP_SET_LOCAL_NAME is handled asynchronously on powered controllers
and can run set_name_sync().  When the controller is BR/EDR capable,
set_name_sync() updates the local name and then rebuilds EIR data through
eir_create().  The EIR builder walks hdev->uuids, but the UUID list can
be changed and entries can be freed by MGMT_OP_ADD_UUID and
MGMT_OP_REMOVE_UUID.

pending_eir_or_class() is meant to serialize management commands that
can change EIR or the class of device, but it did not include
MGMT_OP_SET_LOCAL_NAME.  In addition, it walked hdev->mgmt_pending
without hdev->mgmt_pending_lock even though pending commands are added
and removed under that mutex.  A racing command completion can therefore
remove and free a pending command while pending_eir_or_class() is still
inspecting it, leading to a use-after-free in the pending-command list or
allowing a local name update to rebuild EIR while UUID entries are being
removed.

Take hdev->mgmt_pending_lock while scanning hdev->mgmt_pending and treat
MGMT_OP_SET_LOCAL_NAME as an EIR/class-affecting pending command on the
powered asynchronous path.  Check for a conflicting pending command before
copying the new short name so a rejected SET_LOCAL_NAME request does not
modify hdev->short_name.

## References
- https://git.kernel.org/stable/c/35464ff818165131464bd524c259db1ac8044ae3
- https://git.kernel.org/stable/c/814f82f432dc6ee4d15f94756554ff94e6e3ef05
- https://git.kernel.org/stable/c/8f2f62855a41d1730fb9e8122912bd2c8d6bed5d
- https://git.kernel.org/stable/c/a9e7c2609b0cb3fb4b4ba9f66dd8727d33205967
- https://git.kernel.org/stable/c/eacfcb6b735d0e16b4d2ecfde4b9141225ee934e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74511.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74511
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
