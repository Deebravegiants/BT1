# [C] scsi: qla2xxx: Fix improper freeing of purex item

## Summary
Severity: Critical
Advisory: CVE-2025-68741
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-24
Source: https://osv.dev/vulnerability/CVE-2025-68741
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.6.0 <6.6.120, >=6.7.0 <6.12.63, >=6.13.0 <6.17.13, >=6.18.0 <6.18.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: qla2xxx: Fix improper freeing of purex item

In qla2xxx_process_purls_iocb(), an item is allocated via
qla27xx_copy_multiple_pkt(), which internally calls
qla24xx_alloc_purex_item().

The qla24xx_alloc_purex_item() function may return a pre-allocated item
from a per-adapter pool for small allocations, instead of dynamically
allocating memory with kzalloc().

An error handling path in qla2xxx_process_purls_iocb() incorrectly uses
kfree() to release the item. If the item was from the pre-allocated
pool, calling kfree() on it is a bug that can lead to memory corruption.

Fix this by using the correct deallocation function,
qla24xx_free_purex_item(), which properly handles both dynamically
allocated and pre-allocated items.

## References
- https://git.kernel.org/stable/c/4bccd506a1f1ab01d1f45b2a3effff6bedc73cf9
- https://git.kernel.org/stable/c/5fa1c8226b4532ad7011d295d3ab4ad45df105ae
- https://git.kernel.org/stable/c/78b1a242fe612a755f2158fd206ee6bb577d18ca
- https://git.kernel.org/stable/c/8e9f0a0717ba31d5842721627ade1e62d7aec012
- https://git.kernel.org/stable/c/cfe3e2f768d248fd3d965d561d0768a56dd0b9f8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68741.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-68741
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
