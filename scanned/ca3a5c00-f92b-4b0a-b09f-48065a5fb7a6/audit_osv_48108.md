# [H] CVE-2017-18220

## Summary
Severity: High
Advisory: CVE-2017-18220
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-03-05
Source: https://osv.dev/vulnerability/CVE-2017-18220
Type: osv

## Details
The ReadOneJNGImage and ReadJNGImage functions in coders/png.c in GraphicsMagick 1.3.26 allow remote attackers to cause a denial of service (magick/blob.c CloseBlob use-after-free) or possibly have unspecified other impact via a crafted file, a related issue to CVE-2017-11403.

## References
- https://lists.debian.org/debian-lts-announce/2018/03/msg00025.html
- https://lists.debian.org/debian-lts-announce/2018/08/msg00002.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PF62B5PJA2JDUOCKJGUQO3SPL74BEYSV/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WHIKB4TP6KBJWT2UIPWL5MWMG5QXKGEJ/
- https://www.debian.org/security/2018/dsa-4321
- http://www.securityfocus.com/bid/103276
- https://sourceforge.net/p/graphicsmagick/bugs/438/
- http://hg.graphicsmagick.org/hg/GraphicsMagick/rev/98721124e51f
