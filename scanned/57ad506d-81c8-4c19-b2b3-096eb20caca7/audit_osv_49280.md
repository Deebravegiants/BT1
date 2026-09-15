# [H] CVE-2018-8804

## Summary
Severity: High
Advisory: CVE-2018-8804
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-03-20
Source: https://osv.dev/vulnerability/CVE-2018-8804
Type: osv

## Details
WriteEPTImage in coders/ept.c in ImageMagick 7.0.7-25 Q16 allows remote attackers to cause a denial of service (MagickCore/memory.c double free and application crash) or possibly have unspecified other impact via a crafted file.

## References
- https://lists.debian.org/debian-lts-announce/2020/08/msg00030.html
- http://www.securityfocus.com/bid/103498
- https://usn.ubuntu.com/3681-1/
- https://github.com/ImageMagick/ImageMagick/issues/1025
