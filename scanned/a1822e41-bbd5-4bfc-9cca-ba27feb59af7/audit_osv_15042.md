# [H] CVE-2019-13103

## Summary
Severity: High
Advisory: CVE-2019-13103
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2019-07-29
Source: https://osv.dev/vulnerability/CVE-2019-13103
Type: osv

## Details
A crafted self-referential DOS partition table will cause all Das U-Boot versions through 2019.07-rc4 to infinitely recurse, causing the stack to grow infinitely and eventually either crash or overwrite other data.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-577017.html
- https://cert-portal.siemens.com/productcert/html/ssa-618620.html
- https://cert-portal.siemens.com/productcert/pdf/ssa-618620.pdf
- https://gist.github.com/deephooloovoo/d91b81a1674b4750e662dfae93804d75
- https://github.com/u-boot/u-boot/commits/master
- https://lists.denx.de/pipermail/u-boot/2019-July/375512.html
