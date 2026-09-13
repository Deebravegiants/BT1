# [H] CVE-2017-12935

## Summary
Severity: High
Advisory: CVE-2017-12935
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-08-18
Source: https://osv.dev/vulnerability/CVE-2017-12935
Type: osv

## Details
The ReadMNGImage function in coders/png.c in GraphicsMagick 1.3.26 mishandles large MNG images, leading to an invalid memory read in the SetImageColorCallBack function in magick/image.c.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PF62B5PJA2JDUOCKJGUQO3SPL74BEYSV/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WHIKB4TP6KBJWT2UIPWL5MWMG5QXKGEJ/
- https://usn.ubuntu.com/4222-1/
- https://lists.debian.org/debian-lts-announce/2018/08/msg00002.html
- https://www.debian.org/security/2018/dsa-4321
- https://blogs.gentoo.org/ago/2017/08/05/graphicsmagick-invalid-memory-read-in-setimagecolorcallback-image-c/
- http://hg.code.sf.net/p/graphicsmagick/code/rev/cd699a44f188
