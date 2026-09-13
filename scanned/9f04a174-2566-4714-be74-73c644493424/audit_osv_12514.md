# [H] CVE-2018-12599

## Summary
Severity: High
Advisory: CVE-2018-12599
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-06-20
Source: https://osv.dev/vulnerability/CVE-2018-12599
Type: osv

## Details
In ImageMagick 7.0.8-3 Q16, ReadBMPImage and WriteBMPImage in coders/bmp.c allow attackers to cause an out of bounds write via a crafted file.

## References
- https://lists.debian.org/debian-lts-announce/2018/06/msg00004.html
- https://usn.ubuntu.com/3711-1/
- https://www.debian.org/security/2018/dsa-4245
- https://github.com/ImageMagick/ImageMagick/issues/1177
