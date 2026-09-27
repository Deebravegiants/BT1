# [H] CVE-2017-17498

## Summary
Severity: High
Advisory: CVE-2017-17498
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-12-11
Source: https://osv.dev/vulnerability/CVE-2017-17498
Type: osv

## Details
WritePNMImage in coders/pnm.c in GraphicsMagick 1.3.26 allows remote attackers to cause a denial of service (bit_stream.c MagickBitStreamMSBWrite heap-based buffer overflow and application crash) or possibly have unspecified other impact via a crafted file.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PF62B5PJA2JDUOCKJGUQO3SPL74BEYSV/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WHIKB4TP6KBJWT2UIPWL5MWMG5QXKGEJ/
- https://usn.ubuntu.com/4248-1/
- https://lists.debian.org/debian-lts-announce/2018/01/msg00005.html
- https://lists.debian.org/debian-lts-announce/2018/06/msg00009.html
- https://www.debian.org/security/2018/dsa-4321
- http://www.securityfocus.com/bid/102158
- https://sourceforge.net/p/graphicsmagick/bugs/525/
- http://hg.code.sf.net/p/graphicsmagick/code/rev/f1c418ef0260
