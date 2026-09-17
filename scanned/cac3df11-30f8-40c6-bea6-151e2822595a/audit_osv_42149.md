# [C] smb: client: fix double-free in SMB2_close() replay

## Summary
Severity: Critical
Advisory: CVE-2026-64597
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-06
Source: https://osv.dev/vulnerability/CVE-2026-64597
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.6.145, >=6.7.0 <6.12.96, >=6.8.0 <6.18.39, >=6.13.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

smb: client: fix double-free in SMB2_close() replay

A response-bearing attempt can return a replayable error and free its
response buffer. If SMB2_close_init() fails before the next send, cleanup
retains the previous buffer type and frees that response again.

Reset response bookkeeping before each attempt to prevent the stale free.

## References
- https://git.kernel.org/stable/c/037511726228aaf165c7067ff2bfc88eaecdf1f3
- https://git.kernel.org/stable/c/0aa97edf7c347c0f54e7e60c4740574b8120c66a
- https://git.kernel.org/stable/c/b18ed621dbfceecea5539848cddcb9272c9a61e1
- https://git.kernel.org/stable/c/d15d83125007f673aec4323e1bbbaaffbe87ea13
- https://git.kernel.org/stable/c/f96e1cdcb63ed3321142ff2fcdf784e32cda8fee
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64597.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64597
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
