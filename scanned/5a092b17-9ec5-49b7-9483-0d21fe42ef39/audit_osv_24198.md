# [M] fbdev: fbcon: release buffer when fbcon_do_set_font() failed

## Summary
Severity: Medium
Advisory: CVE-2022-50404
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-18
Source: https://osv.dev/vulnerability/CVE-2022-50404
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.15.86, >=5.16.0 <6.0.16, >=6.0.0 <6.1.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

fbdev: fbcon: release buffer when fbcon_do_set_font() failed

syzbot is reporting memory leak at fbcon_do_set_font() [1], for
commit a5a923038d70 ("fbdev: fbcon: Properly revert changes when
vc_resize() failed") missed that the buffer might be newly allocated
by fbcon_set_font().

## References
- https://git.kernel.org/stable/c/06926607b9fddf7ce8017493899ce6eb7e79a123
- https://git.kernel.org/stable/c/3c3bfb8586f848317ceba5d777e11204ba3e5758
- https://git.kernel.org/stable/c/5a341810a22e51c3a7a108f7896b5fd58d44d127
- https://git.kernel.org/stable/c/88ec6d11052da527eb9268831e7a9bc5bbad02f6
- https://git.kernel.org/stable/c/a609bfc1e644a8467cb31945ed1488374ebdc013
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50404.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50404
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
