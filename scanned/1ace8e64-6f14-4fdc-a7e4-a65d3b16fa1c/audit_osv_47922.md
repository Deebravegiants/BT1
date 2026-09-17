# [M] CVE-2017-14997

## Summary
Severity: Medium
Advisory: CVE-2017-14997
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-10-04
Source: https://osv.dev/vulnerability/CVE-2017-14997
Type: osv

## Details
GraphicsMagick 1.3.26 allows remote attackers to cause a denial of service (excessive memory allocation) because of an integer underflow in ReadPICTImage in coders/pict.c.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PF62B5PJA2JDUOCKJGUQO3SPL74BEYSV/
- https://usn.ubuntu.com/4232-1/
- http://hg.graphicsmagick.org/hg/GraphicsMagick?cmd=changeset%3Bnode=0683f8724200
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WHIKB4TP6KBJWT2UIPWL5MWMG5QXKGEJ/
- https://lists.debian.org/debian-lts-announce/2018/08/msg00002.html
- https://www.debian.org/security/2018/dsa-4321
- http://www.securityfocus.com/bid/101183
- https://sourceforge.net/p/graphicsmagick/bugs/511/
- https://sourceforge.net/p/graphicsmagick/code/ci/0683f8724200495059606c03f04e0d589b33ebe8/
