# [M] CVE-2017-14314

## Summary
Severity: Medium
Advisory: CVE-2017-14314
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-09-12
Source: https://osv.dev/vulnerability/CVE-2017-14314
Type: osv

## Details
Off-by-one error in the DrawImage function in magick/render.c in GraphicsMagick 1.3.26 allows remote attackers to cause a denial of service (DrawDashPolygon heap-based buffer over-read and application crash) via a crafted file.

## References
- https://usn.ubuntu.com/4232-1/
- https://lists.debian.org/debian-lts-announce/2018/06/msg00009.html
- https://www.debian.org/security/2018/dsa-4321
- http://hg.code.sf.net/p/graphicsmagick/code/rev/2835184bfb78
- https://sourceforge.net/p/graphicsmagick/bugs/448/
