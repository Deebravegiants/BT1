# [H] CVE-2018-8960

## Summary
Severity: High
Advisory: CVE-2018-8960
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-03-23
Source: https://osv.dev/vulnerability/CVE-2018-8960
Type: osv

## Details
The ReadTIFFImage function in coders/tiff.c in ImageMagick 7.0.7-26 Q16 does not properly restrict memory allocation, leading to a heap-based buffer over-read.

## References
- https://lists.debian.org/debian-lts-announce/2020/08/msg00030.html
- http://www.securityfocus.com/bid/103523
- https://usn.ubuntu.com/3681-1/
- https://github.com/ImageMagick/ImageMagick/issues/1020
