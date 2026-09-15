# [H] CVE-2017-15930

## Summary
Severity: High
Advisory: CVE-2017-15930
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-10-27
Source: https://osv.dev/vulnerability/CVE-2017-15930
Type: osv

## Details
In ReadOneJNGImage in coders/png.c in GraphicsMagick 1.3.26, a Null Pointer Dereference occurs while transferring JPEG scanlines, related to a PixelPacket pointer.

## References
- http://hg.graphicsmagick.org/hg/GraphicsMagick?cmd=changeset%3Bnode=6fc54b6d2be8
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PF62B5PJA2JDUOCKJGUQO3SPL74BEYSV/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WHIKB4TP6KBJWT2UIPWL5MWMG5QXKGEJ/
- http://hg.graphicsmagick.org/hg/GraphicsMagick?cmd=changeset%3Bnode=da135eaedc3b
- https://usn.ubuntu.com/4232-1/
- https://lists.debian.org/debian-lts-announce/2018/08/msg00002.html
- https://www.debian.org/security/2018/dsa-4321
- http://www.securityfocus.com/bid/101607
- https://sourceforge.net/p/graphicsmagick/bugs/518/
