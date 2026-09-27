# [H] erofs: fix the out-of-bounds nameoff handling for trailing dirents

## Summary
Severity: High
Advisory: CVE-2026-46078
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-46078
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.19.0 <5.10.259, >=5.11.0 <5.15.210, >=5.16.0 <6.1.175, >=6.2.0 <6.6.140, >=6.7.0 <6.12.86, >=6.13.0 <6.18.27, >=6.19.0 <7.0.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

erofs: fix the out-of-bounds nameoff handling for trailing dirents

Currently we already have boundary-checks for nameoffs, but the trailing
dirents are special since the namelens are calculated with strnlen()
with unchecked nameoffs.

If a crafted EROFS has a trailing dirent with nameoff >= maxsize,
maxsize - nameoff can underflow, causing strnlen() to read past the
directory block.

nameoff0 should also be verified to be a multiple of
`sizeof(struct erofs_dirent)` as well [1].

[1] https://sashiko.dev/#/patchset/20260416063511.3173774-1-hsiangkao%40linux.alibaba.com

## References
- https://git.kernel.org/stable/c/1d55445226c75ddd4e78b09b3e7d99109b28c366
- https://git.kernel.org/stable/c/222055e6b4063abd2d9e13c3d49bbd1724c50789
- https://git.kernel.org/stable/c/48b27a955d22391c7f30169fa7b6b2e1977f1ce4
- https://git.kernel.org/stable/c/80a23c6d1aba35be8746d74ac14e6ba5ae46da21
- https://git.kernel.org/stable/c/8ebb951a284b7446e025afc7dc5e9516ef9a7214
- https://git.kernel.org/stable/c/a8ee527807f7d97e55ce2ef2906f7f34975eb1c7
- https://git.kernel.org/stable/c/aa16dca1b062355181ef215229eeac249d7c0d61
- https://git.kernel.org/stable/c/d18a3b5d337fa412a38e776e6b4b857a58836575
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46078.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46078
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
