# [M] CVE-2017-13134

## Summary
Severity: Medium
Advisory: CVE-2017-13134
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-08-23
Source: https://osv.dev/vulnerability/CVE-2017-13134
Type: osv

## Details
In ImageMagick 7.0.6-6 and GraphicsMagick 1.3.26, a heap-based buffer over-read was found in the function SFWScan in coders/sfw.c, which allows attackers to cause a denial of service via a crafted file.

## References
- http://hg.code.sf.net/p/graphicsmagick/code/rev/1b47e0078e05
- http://www.securityfocus.com/bid/100476
- https://lists.debian.org/debian-lts-announce/2017/11/msg00016.html
- https://lists.debian.org/debian-lts-announce/2018/06/msg00009.html
- https://usn.ubuntu.com/3681-1/
- https://usn.ubuntu.com/4222-1/
- https://security.gentoo.org/glsa/201711-07
- https://www.debian.org/security/2017/dsa-4032
- https://www.debian.org/security/2017/dsa-4040
- https://www.debian.org/security/2018/dsa-4321
- https://github.com/ImageMagick/ImageMagick/issues/670
