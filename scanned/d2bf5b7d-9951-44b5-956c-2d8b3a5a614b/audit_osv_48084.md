# [H] CVE-2017-17912

## Summary
Severity: High
Advisory: CVE-2017-17912
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-12-27
Source: https://osv.dev/vulnerability/CVE-2017-17912
Type: osv

## Details
In GraphicsMagick 1.4 snapshot-20171217 Q8, there is a heap-based buffer over-read in ReadNewsProfile in coders/tiff.c, in which LocaleNCompare reads heap data beyond the allocated region.

## References
- https://usn.ubuntu.com/4266-1/
- https://lists.debian.org/debian-lts-announce/2018/01/msg00005.html
- https://lists.debian.org/debian-lts-announce/2018/06/msg00009.html
- https://www.debian.org/security/2018/dsa-4321
- https://sourceforge.net/p/graphicsmagick/bugs/533/
- http://hg.graphicsmagick.org/hg/GraphicsMagick/rev/0d871e813a4f
