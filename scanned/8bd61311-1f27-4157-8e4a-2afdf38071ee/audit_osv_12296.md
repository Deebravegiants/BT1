# [M] CVE-2018-11251

## Summary
Severity: Medium
Advisory: CVE-2018-11251
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-05-18
Source: https://osv.dev/vulnerability/CVE-2018-11251
Type: osv

## Details
In ImageMagick 7.0.7-23 Q16 x86_64 2018-01-24, there is a heap-based buffer over-read in ReadSUNImage in coders/sun.c, which allows attackers to cause a denial of service (application crash in SetGrayscaleImage in MagickCore/quantize.c) via a crafted SUN image file.

## References
- https://lists.debian.org/debian-lts-announce/2018/06/msg00004.html
- https://lists.debian.org/debian-lts-announce/2018/05/msg00012.html
- https://usn.ubuntu.com/3681-1/
- https://www.debian.org/security/2018/dsa-4245
- https://github.com/ImageMagick/ImageMagick/issues/956
