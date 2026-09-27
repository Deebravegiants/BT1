# [H] scsi: Revert "scsi: core: Do not increase scsi_device's iorequest_cnt if dispatch failed"

## Summary
Severity: High
Advisory: CVE-2023-53609
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-04
Source: https://osv.dev/vulnerability/CVE-2023-53609
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.2.0 <6.3.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: Revert "scsi: core: Do not increase scsi_device's iorequest_cnt if dispatch failed"

The "atomic_inc(&cmd->device->iorequest_cnt)" in scsi_queue_rq() would
cause kernel panic because cmd->device may be freed after returning from
scsi_dispatch_cmd().

This reverts commit cfee29ffb45b1c9798011b19d454637d1b0fe87d.

## References
- https://git.kernel.org/stable/c/35fe6fa57b994e7da222893adf0bb748d6055e73
- https://git.kernel.org/stable/c/6ca9818d1624e136a76ae8faedb6b6c95ca66903
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53609.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53609
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
