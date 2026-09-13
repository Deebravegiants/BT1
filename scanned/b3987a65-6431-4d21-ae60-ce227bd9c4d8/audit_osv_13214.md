# [M] CVE-2018-18661

## Summary
Severity: Medium
Advisory: CVE-2018-18661
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-10-26
Source: https://osv.dev/vulnerability/CVE-2018-18661
Type: osv

## Details
An issue was discovered in LibTIFF 4.0.9. There is a NULL pointer dereference in the function LZWDecode in the file tif_lzw.c.

## References
- https://lists.debian.org/debian-lts-announce/2019/11/msg00027.html
- http://www.securityfocus.com/bid/105762
- https://access.redhat.com/errata/RHSA-2019:2053
- https://usn.ubuntu.com/3864-1/
- http://bugzilla.maptools.org/show_bug.cgi?id=2819
