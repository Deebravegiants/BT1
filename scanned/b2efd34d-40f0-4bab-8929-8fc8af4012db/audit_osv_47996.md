# [H] CVE-2017-16545

## Summary
Severity: High
Advisory: CVE-2017-16545
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-11-05
Source: https://osv.dev/vulnerability/CVE-2017-16545
Type: osv

## Details
The ReadWPGImage function in coders/wpg.c in GraphicsMagick 1.3.26 does not properly validate colormapped images, which allows remote attackers to cause a denial of service (ImportIndexQuantumType invalid write and application crash) or possibly have unspecified other impact via a malformed WPG image.

## References
- https://lists.debian.org/debian-lts-announce/2018/08/msg00002.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PF62B5PJA2JDUOCKJGUQO3SPL74BEYSV/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WHIKB4TP6KBJWT2UIPWL5MWMG5QXKGEJ/
- https://usn.ubuntu.com/4248-1/
- https://www.debian.org/security/2018/dsa-4321
- http://hg.code.sf.net/p/graphicsmagick/code/rev/e8086faa52d0
- https://sourceforge.net/p/graphicsmagick/bugs/519/
