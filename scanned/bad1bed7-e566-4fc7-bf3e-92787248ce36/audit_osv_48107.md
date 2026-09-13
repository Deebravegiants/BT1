# [M] CVE-2017-18219

## Summary
Severity: Medium
Advisory: CVE-2017-18219
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-03-05
Source: https://osv.dev/vulnerability/CVE-2017-18219
Type: osv

## Details
An issue was discovered in GraphicsMagick 1.3.26. An allocation failure vulnerability was found in the function ReadOnePNGImage in coders/png.c, which allows attackers to cause a denial of service via a crafted file that triggers an attempt at a large png_pixels array allocation.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WHIKB4TP6KBJWT2UIPWL5MWMG5QXKGEJ/
- https://usn.ubuntu.com/4266-1/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PF62B5PJA2JDUOCKJGUQO3SPL74BEYSV/
- https://www.debian.org/security/2018/dsa-4321
- https://lists.debian.org/debian-lts-announce/2018/03/msg00025.html
- https://lists.debian.org/debian-lts-announce/2018/08/msg00002.html
- http://www.securityfocus.com/bid/103258
- https://sourceforge.net/p/graphicsmagick/bugs/459/
- http://hg.graphicsmagick.org/hg/GraphicsMagick/rev/cadd4b0522fa
