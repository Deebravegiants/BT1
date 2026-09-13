# [H] f2fs: fix potential corruption when moving a directory

## Summary
Severity: High
Advisory: CVE-2023-54187
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-30
Source: https://osv.dev/vulnerability/CVE-2023-54187
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.19.0 <5.4.243, >=5.5.0 <5.10.180, >=5.11.0 <5.15.112, >=5.16.0 <6.1.29, >=6.2.0 <6.2.16, >=6.3.0 <6.3.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

f2fs: fix potential corruption when moving a directory

F2FS has the same issue in ext4_rename causing crash revealed by
xfstests/generic/707.

See also commit 0813299c586b ("ext4: Fix possible corruption when moving a directory")

## References
- https://git.kernel.org/stable/c/0a76082a4a32a90d1ef33dee8b400efc082b4b6f
- https://git.kernel.org/stable/c/3e77036246123ff710fa2661dcaa12a45284f09b
- https://git.kernel.org/stable/c/8a0b544b7caedfbc05065b6377fd1d8bf7ef5e70
- https://git.kernel.org/stable/c/8f57f3e112cf1d16682b6ff9c31c72f40f7da9c9
- https://git.kernel.org/stable/c/957904f531fd857a92743b11fbc9c9ffdf7f3207
- https://git.kernel.org/stable/c/d94772154e524b329a168678836745d2773a6e02
- https://git.kernel.org/stable/c/f20191100952013f0916418cdaed0ab55c7b634c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/54xxx/CVE-2023-54187.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-54187
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
