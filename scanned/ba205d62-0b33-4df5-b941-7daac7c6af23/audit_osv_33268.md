# [C] smb: client: fix wrong index reference in smb2_compound_op()

## Summary
Severity: Critical
Advisory: CVE-2025-39975
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-15
Source: https://osv.dev/vulnerability/CVE-2025-39975
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.6.109, >=6.7.0 <6.12.50, >=6.13.0 <6.16.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

smb: client: fix wrong index reference in smb2_compound_op()

In smb2_compound_op(), the loop that processes each command's response
uses wrong indices when accessing response bufferes.

This incorrect indexing leads to improper handling of command results.
Also, if incorrectly computed index is greather than or equal to
MAX_COMPOUND, it can cause out-of-bounds accesses.

## References
- https://git.kernel.org/stable/c/093615fc76063ea08d454ba86677ce64c736e806
- https://git.kernel.org/stable/c/ba7bcfd52c66dd1c2dfa5142aca7e4a70b62dfa5
- https://git.kernel.org/stable/c/bfb1e2aad1fecef8320fd71332acde0d53a8d699
- https://git.kernel.org/stable/c/fbe2dc6a9c7318f7263f5e4d50f6272b931c5756
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39975.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39975
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
