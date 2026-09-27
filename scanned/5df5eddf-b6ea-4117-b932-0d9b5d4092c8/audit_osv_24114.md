# [C] NFSD: Protect against send buffer overflow in NFSv2 READDIR

## Summary
Severity: Critical
Advisory: CVE-2022-50235
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-15
Source: https://osv.dev/vulnerability/CVE-2022-50235
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.15.75, >=5.16.0 <6.0.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

NFSD: Protect against send buffer overflow in NFSv2 READDIR

Restore the previous limit on the @count argument to prevent a
buffer overflow attack.

## References
- https://git.kernel.org/stable/c/00b4492686e0497fdb924a9d4c8f6f99377e176c
- https://git.kernel.org/stable/c/0e57d696f60dee6117a8ace0cac7c5761d375277
- https://git.kernel.org/stable/c/c2a878095b5c6f04f90553a3c45872f990dab14e
- https://git.kernel.org/stable/c/dc7f225090c29a5f3b9419b1af32846a201555e7
- https://git.kernel.org/stable/c/f59c74df82f6ac9d2ea4e01aa3ae7c6c4481652d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50235.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50235
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
