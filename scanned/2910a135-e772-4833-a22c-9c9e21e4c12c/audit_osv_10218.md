# [M] CVE-2017-14341

## Summary
Severity: Medium
Advisory: CVE-2017-14341
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-09-12
Source: https://osv.dev/vulnerability/CVE-2017-14341
Type: osv

## Details
ImageMagick 7.0.6-6 has a large loop vulnerability in ReadWPGImage in coders/wpg.c, causing CPU exhaustion via a crafted wpg image file.

## References
- https://lists.debian.org/debian-lts-announce/2019/05/msg00015.html
- https://lists.debian.org/debian-lts-announce/2020/09/msg00007.html
- https://usn.ubuntu.com/3681-1/
- https://github.com/ImageMagick/ImageMagick/commit/7d63315a64267c565d1f34b9cb523a14616fed24
- https://github.com/ImageMagick/ImageMagick/issues/654
