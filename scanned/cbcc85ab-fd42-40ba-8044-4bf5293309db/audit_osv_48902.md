# [M] CVE-2018-18024

## Summary
Severity: Medium
Advisory: CVE-2018-18024
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-10-07
Source: https://osv.dev/vulnerability/CVE-2018-18024
Type: osv

## Details
In ImageMagick 7.0.8-13 Q16, there is an infinite loop in the ReadBMPImage function of the coders/bmp.c file. Remote attackers could leverage this vulnerability to cause a denial of service via a crafted bmp file.

## References
- https://lists.debian.org/debian-lts-announce/2020/08/msg00030.html
- https://usn.ubuntu.com/4034-1/
- https://github.com/ImageMagick/ImageMagick/issues/1337
