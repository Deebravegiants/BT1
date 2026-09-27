# [H] CVE-2019-13104

## Summary
Severity: High
Advisory: CVE-2019-13104
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-08-06
Source: https://osv.dev/vulnerability/CVE-2019-13104
Type: osv

## Details
In Das U-Boot versions 2016.11-rc1 through 2019.07-rc4, an underflow can cause memcpy() to overwrite a very large amount of data (including the whole stack) while reading a crafted ext4 filesystem.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-577017.html
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00002.html
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00004.html
- https://gist.github.com/deephooloovoo/d91b81a1674b4750e662dfae93804d75
- https://github.com/u-boot/u-boot/commits/master
- https://lists.denx.de/pipermail/u-boot/2019-July/375514.html
