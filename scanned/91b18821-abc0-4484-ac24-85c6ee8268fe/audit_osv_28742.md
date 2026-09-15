# [H] i40e: fix vf may be used uninitialized in this function warning

## Summary
Severity: High
Advisory: CVE-2024-36020
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-30
Source: https://osv.dev/vulnerability/CVE-2024-36020
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <4.19.312, >=4.20.0 <5.4.274, >=5.5.0 <5.10.215, >=5.11.0 <5.15.154, >=5.16.0 <6.1.85, >=6.1.0 <6.6.26, >=6.2.0 <6.8.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

i40e: fix vf may be used uninitialized in this function warning

To fix the regression introduced by commit 52424f974bc5, which causes
servers hang in very hard to reproduce conditions with resets races.
Using two sources for the information is the root cause.
In this function before the fix bumping v didn't mean bumping vf
pointer. But the code used this variables interchangeably, so stale vf
could point to different/not intended vf.

Remove redundant "v" variable and iterate via single VF pointer across
whole function instead to guarantee VF pointer validity.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/06df7618f591b2dc43c59967e294d7b9fc8675b6
- https://git.kernel.org/stable/c/0dcf573f997732702917af1563aa2493dc772fc0
- https://git.kernel.org/stable/c/3e89846283f3cf7c7a8e28b342576fd7c561d2ba
- https://git.kernel.org/stable/c/951d2748a2a8242853abc3d0c153ce4bf8faad31
- https://git.kernel.org/stable/c/9dcf0fcb80f6aeb01469e3c957f8d4c97365450a
- https://git.kernel.org/stable/c/b8e82128b44fa40bf99a50b919488ef361e1683c
- https://git.kernel.org/stable/c/cc9cd02dd9e8b7764ea9effb24f4f1dd73d1b23d
- https://git.kernel.org/stable/c/f37c4eac99c258111d414d31b740437e1925b8e8
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/36xxx/CVE-2024-36020.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-36020
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
