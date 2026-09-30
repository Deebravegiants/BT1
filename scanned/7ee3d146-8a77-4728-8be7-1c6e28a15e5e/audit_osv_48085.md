# [H] CVE-2017-17913

## Summary
Severity: High
Advisory: CVE-2017-17913
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-12-27
Source: https://osv.dev/vulnerability/CVE-2017-17913
Type: osv

## Details
In GraphicsMagick 1.4 snapshot-20171217 Q8, there is a stack-based buffer over-read in WriteWEBPImage in coders/webp.c, related to an incompatibility with libwebp versions, 0.5.0 and later, that use a different structure type.

## References
- https://usn.ubuntu.com/4266-1/
- https://www.debian.org/security/2018/dsa-4321
- https://sourceforge.net/p/graphicsmagick/bugs/536/
- http://hg.graphicsmagick.org/hg/GraphicsMagick/rev/6dda3c33f35f
