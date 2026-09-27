# [H] RDMA/bnxt_re: Add a max slot check for SQ

## Summary
Severity: High
Advisory: CVE-2026-72497
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72497
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/bnxt_re: Add a max slot check for SQ

The variable WQE mode must be validated against
the maximum slots supported by HW. The max supported
value is 64K. Adding a max and min check and fail if user
supplied value is more than the max supported and zero.

## References
- https://git.kernel.org/stable/c/a59d815cbe667929b693b5fa6716a074e6a31c5b
- https://git.kernel.org/stable/c/dc95931b7e1326dacae547874bf38c092e5960d8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72497.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72497
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
