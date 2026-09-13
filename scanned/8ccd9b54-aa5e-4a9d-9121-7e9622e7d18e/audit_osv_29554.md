# [H] RDMA/hns: Fix soft lockup under heavy CEQE load

## Summary
Severity: High
Advisory: CVE-2024-43872
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-08-21
Source: https://osv.dev/vulnerability/CVE-2024-43872
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.16.0 <6.10.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/hns: Fix soft lockup under heavy CEQE load

CEQEs are handled in interrupt handler currently. This may cause the
CPU core staying in interrupt context too long and lead to soft lockup
under heavy load.

Handle CEQEs in BH workqueue and set an upper limit for the number of
CEQE handled by a single call of work handler.

## References
- https://git.kernel.org/stable/c/06580b33c183c9f98e2a2ca96a86137179032c08
- https://git.kernel.org/stable/c/2fdf34038369c0a27811e7b4680662a14ada1d6b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/43xxx/CVE-2024-43872.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-43872
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
