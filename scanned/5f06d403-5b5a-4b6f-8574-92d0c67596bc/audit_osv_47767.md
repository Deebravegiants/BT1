# [H] CVE-2017-11638

## Summary
Severity: High
Advisory: CVE-2017-11638
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-07-26
Source: https://osv.dev/vulnerability/CVE-2017-11638
Type: osv

## Details
GraphicsMagick 1.3.26 has a segmentation violation in the WriteMAPImage() function in coders/map.c when processing a non-colormapped image, a different vulnerability than CVE-2017-11642.

## References
- https://lists.debian.org/debian-lts-announce/2018/08/msg00002.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PF62B5PJA2JDUOCKJGUQO3SPL74BEYSV/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WHIKB4TP6KBJWT2UIPWL5MWMG5QXKGEJ/
- https://usn.ubuntu.com/4222-1/
- http://hg.code.sf.net/p/graphicsmagick/code/rev/29550606d8b9
- https://www.debian.org/security/2018/dsa-4321
