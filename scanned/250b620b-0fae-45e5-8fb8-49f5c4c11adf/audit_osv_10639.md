# [H] CVE-2017-17879

## Summary
Severity: High
Advisory: CVE-2017-17879
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-12-27
Source: https://osv.dev/vulnerability/CVE-2017-17879
Type: osv

## Details
In ImageMagick 7.0.7-16 Q16 x86_64 2017-12-21, there is a heap-based buffer over-read in ReadOneMNGImage in coders/png.c, related to length calculation and caused by an off-by-one error.

## References
- http://www.securityfocus.com/bid/102305
- https://lists.debian.org/debian-lts-announce/2018/01/msg00000.html
- https://usn.ubuntu.com/3681-1/
- https://www.debian.org/security/2017/dsa-4074
- https://www.debian.org/security/2018/dsa-4204
- https://github.com/ImageMagick/ImageMagick/issues/906
