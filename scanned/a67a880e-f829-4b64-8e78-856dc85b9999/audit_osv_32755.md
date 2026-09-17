# [H] eth: bnxt: fix missing ring index trim on error path

## Summary
Severity: High
Advisory: CVE-2025-37873
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-09
Source: https://osv.dev/vulnerability/CVE-2025-37873
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.12.25, >=6.13.0 <6.14.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

eth: bnxt: fix missing ring index trim on error path

Commit under Fixes converted tx_prod to be free running but missed
masking it on the Tx error path. This crashes on error conditions,
for example when DMA mapping fails.

## References
- https://git.kernel.org/stable/c/12f2d033fae957d84c2c0ce604d2a077e61fa2c0
- https://git.kernel.org/stable/c/21e70f694bc0dcb40174b0940cc52a7769fc19e0
- https://git.kernel.org/stable/c/3742c55de00266fa7c8fd2c5d61a453d223a9cd1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/37xxx/CVE-2025-37873.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-37873
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
