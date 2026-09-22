# [H] RDMA/bnxt_re: Add a check for memory allocation

## Summary
Severity: High
Advisory: CVE-2024-50209
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-08
Source: https://osv.dev/vulnerability/CVE-2024-50209
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.7.0 <5.10.229, >=5.11.0 <5.15.170, >=5.16.0 <6.1.115, >=6.2.0 <6.6.59, >=6.7.0 <6.11.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/bnxt_re: Add a check for memory allocation

__alloc_pbl() can return error when memory allocation fails.
Driver is not checking the status on one of the instances.

## References
- https://git.kernel.org/stable/c/322a19baaaa25a1fe8ce9fceaed9409ad847844c
- https://git.kernel.org/stable/c/76dd679c3b148d23f72dcf6c3cde3d5f746b2c07
- https://git.kernel.org/stable/c/ba9045887b435a4c5551245ae034b8791b4e4aaa
- https://git.kernel.org/stable/c/c5c1ae73b7741fa3b58e6e001b407825bb971225
- https://git.kernel.org/stable/c/c71957271f2e8133a6aa82001c2fa671d5008129
- https://git.kernel.org/stable/c/dbe51dd516e6d4e655f31c8a1cbc050dde7ba97b
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50209.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50209
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
