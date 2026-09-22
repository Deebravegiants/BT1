# [M] CVE-2017-14504

## Summary
Severity: Medium
Advisory: CVE-2017-14504
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-09-17
Source: https://osv.dev/vulnerability/CVE-2017-14504
Type: osv

## Details
ReadPNMImage in coders/pnm.c in GraphicsMagick 1.3.26 does not ensure the correct number of colors for the XV 332 format, leading to a NULL Pointer Dereference.

## References
- http://hg.graphicsmagick.org/hg/GraphicsMagick?cmd=changeset%3Bnode=fb09ca6dd22c
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WHIKB4TP6KBJWT2UIPWL5MWMG5QXKGEJ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PF62B5PJA2JDUOCKJGUQO3SPL74BEYSV/
- https://usn.ubuntu.com/4232-1/
- https://www.debian.org/security/2018/dsa-4321
- http://www.securityfocus.com/bid/100877
- https://lists.debian.org/debian-lts-announce/2018/08/msg00002.html
- https://sourceforge.net/p/graphicsmagick/bugs/465/
- https://sourceforge.net/p/graphicsmagick/bugs/466/
