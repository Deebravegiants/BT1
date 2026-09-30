# [H] RDMA/hns: Fix unlocked call to hns_roce_qp_remove()

## Summary
Severity: High
Advisory: CVE-2026-46112
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-28
Source: https://osv.dev/vulnerability/CVE-2026-46112
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.17.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.140, >=6.7.0 <6.12.88, >=6.13.0 <6.18.30, >=6.19.0 <7.0.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/hns: Fix unlocked call to hns_roce_qp_remove()

Sashiko points out that hns_roce_qp_remove() requires the caller to hold
locks.  The error flow in hns_roce_create_qp_common() doesn't hold those
locks for the error unwind so it risks corrupting memory.

Grab the same locks the other two callers use.

## References
- https://git.kernel.org/stable/c/0c99acbc8b6c6dd526ae475a48ee1897b61072fb
- https://git.kernel.org/stable/c/1912f78798505dc9c637081bbddfbf1c22494c49
- https://git.kernel.org/stable/c/1f0a3aa8b569d010316b427238222c5d899f9618
- https://git.kernel.org/stable/c/615d9d260c32bb678504ca96f29ae46f9d745155
- https://git.kernel.org/stable/c/b6296ff2475fc95ee6ea1b528c4b385302808186
- https://git.kernel.org/stable/c/fb4ae739811d467409bd07d0e36cfd4140f3d26a
- https://git.kernel.org/stable/c/fcf6a832c0d5b2bc5398d6996c5570d3ee7993fb
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46112.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46112
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
