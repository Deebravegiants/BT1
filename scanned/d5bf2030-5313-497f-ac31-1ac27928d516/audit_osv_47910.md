# [M] CVE-2017-14649

## Summary
Severity: Medium
Advisory: CVE-2017-14649
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-09-21
Source: https://osv.dev/vulnerability/CVE-2017-14649
Type: osv

## Details
ReadOneJNGImage in coders/png.c in GraphicsMagick version 1.3.26 does not properly validate JNG data, leading to a denial of service (assertion failure in magick/pixel_cache.c, and application crash).

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PF62B5PJA2JDUOCKJGUQO3SPL74BEYSV/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WHIKB4TP6KBJWT2UIPWL5MWMG5QXKGEJ/
- https://usn.ubuntu.com/4232-1/
- http://www.securityfocus.com/bid/100958
- http://hg.code.sf.net/p/graphicsmagick/code/rev/358608a46f0a
- https://blogs.gentoo.org/ago/2017/09/19/graphicsmagick-assertion-failure-in-pixel_cache-c/
- https://sourceforge.net/p/graphicsmagick/bugs/439/
