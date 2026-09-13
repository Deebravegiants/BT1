# [M] CVE-2017-14733

## Summary
Severity: Medium
Advisory: CVE-2017-14733
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-09-25
Source: https://osv.dev/vulnerability/CVE-2017-14733
Type: osv

## Details
ReadRLEImage in coders/rle.c in GraphicsMagick 1.3.26 mishandles RLE headers that specify too few colors, which allows remote attackers to cause a denial of service (heap-based buffer over-read and application crash) via a crafted file.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PF62B5PJA2JDUOCKJGUQO3SPL74BEYSV/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WHIKB4TP6KBJWT2UIPWL5MWMG5QXKGEJ/
- https://sourceforge.net/p/graphicsmagick/bugs/458/
- https://usn.ubuntu.com/4232-1/
- http://hg.graphicsmagick.org/hg/GraphicsMagick?cmd=changeset%3Bnode=5381c71724e3
- https://www.debian.org/security/2018/dsa-4321
- https://lists.debian.org/debian-lts-announce/2018/06/msg00009.html
