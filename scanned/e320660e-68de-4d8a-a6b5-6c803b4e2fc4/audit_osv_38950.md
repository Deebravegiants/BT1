# [H] erofs: fix interlaced plain identification for encoded extents

## Summary
Severity: High
Advisory: CVE-2026-43166
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2026-05-06
Source: https://osv.dev/vulnerability/CVE-2026-43166
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.15.0 <6.18.16, >=6.19.0 <6.19.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

erofs: fix interlaced plain identification for encoded extents

Only plain data whose start position and on-disk physical length are
both aligned to the block size should be classified as interlaced
plain extents. Otherwise, it must be treated as shifted plain extents.

This issue was found by syzbot using a crafted compressed image
containing plain extents with unaligned physical lengths, which can
cause OOB read in z_erofs_transform_plain().

## References
- https://git.kernel.org/stable/c/4a2d046e4b13202a6301a993961f5b30ae4d7119
- https://git.kernel.org/stable/c/9d5a97bc71ed5783687705c708454c4453aa91d1
- https://git.kernel.org/stable/c/d3790f26d38606f020212486359b84632c19d08b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43166.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43166
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
