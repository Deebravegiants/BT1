# [H] CVE-2017-17782

## Summary
Severity: High
Advisory: CVE-2017-17782
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-12-20
Source: https://osv.dev/vulnerability/CVE-2017-17782
Type: osv

## Details
In GraphicsMagick 1.3.27a, there is a heap-based buffer over-read in ReadOneJNGImage in coders/png.c, related to oFFs chunk allocation.

## References
- http://hg.graphicsmagick.org/hg/GraphicsMagick?cmd=changeset%3Bnode=8e3d2264109c
- https://usn.ubuntu.com/4248-1/
- https://lists.debian.org/debian-lts-announce/2018/01/msg00005.html
- https://lists.debian.org/debian-lts-announce/2018/06/msg00009.html
- https://www.debian.org/security/2018/dsa-4321
- https://sourceforge.net/p/graphicsmagick/bugs/530/
