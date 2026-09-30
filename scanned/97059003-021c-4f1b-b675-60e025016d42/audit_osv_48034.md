# [H] CVE-2017-17500

## Summary
Severity: High
Advisory: CVE-2017-17500
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-12-11
Source: https://osv.dev/vulnerability/CVE-2017-17500
Type: osv

## Details
ReadRGBImage in coders/rgb.c in GraphicsMagick 1.3.26 has a magick/import.c ImportRGBQuantumType heap-based buffer over-read via a crafted file.

## References
- https://usn.ubuntu.com/4248-1/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PF62B5PJA2JDUOCKJGUQO3SPL74BEYSV/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WHIKB4TP6KBJWT2UIPWL5MWMG5QXKGEJ/
- https://lists.debian.org/debian-lts-announce/2018/06/msg00009.html
- http://www.securityfocus.com/bid/102164
- https://www.debian.org/security/2018/dsa-4321
- https://lists.debian.org/debian-lts-announce/2018/01/msg00005.html
- https://sourceforge.net/p/graphicsmagick/bugs/523/
- http://hg.code.sf.net/p/graphicsmagick/code/rev/1366f2dd9931
