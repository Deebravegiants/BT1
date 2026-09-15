# [H] RDMA/bnxt_re: Properly order ib_device_unalloc() to avoid UAF

## Summary
Severity: High
Advisory: CVE-2023-53504
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-01
Source: https://osv.dev/vulnerability/CVE-2023-53504
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.3.0 <6.4.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/bnxt_re: Properly order ib_device_unalloc() to avoid UAF

ib_dealloc_device() should be called only after device cleanup.  Fix the
dealloc sequence.

## References
- https://git.kernel.org/stable/c/5363fc488da579923edf6a2fdca3d3b651dd800b
- https://git.kernel.org/stable/c/c95863f6d970ef968e7c1f3c481f72a4b0734654
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53504.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53504
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
