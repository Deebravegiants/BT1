# [H] CVE-2019-13106

## Summary
Severity: High
Advisory: CVE-2019-13106
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-08-06
Source: https://osv.dev/vulnerability/CVE-2019-13106
Type: osv

## Details
Das U-Boot versions 2016.09 through 2019.07-rc4 can memset() too much data while reading a crafted ext4 filesystem, which results in a stack buffer overflow and likely code execution.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-577017.html
- https://github.com/u-boot/u-boot/commits/master
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00002.html
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00004.html
- https://gist.github.com/deephooloovoo/d91b81a1674b4750e662dfae93804d75
- https://lists.denx.de/pipermail/u-boot/2019-July/375516.html
