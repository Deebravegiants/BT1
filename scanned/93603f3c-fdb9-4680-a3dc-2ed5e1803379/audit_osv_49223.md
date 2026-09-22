# [H] CVE-2018-6799

## Summary
Severity: High
Advisory: CVE-2018-6799
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-02-07
Source: https://osv.dev/vulnerability/CVE-2018-6799
Type: osv

## Details
The AcquireCacheNexus function in magick/pixel_cache.c in GraphicsMagick before 1.3.28 allows remote attackers to cause a denial of service (heap overwrite) or possibly have unspecified other impact via a crafted image file, because a pixel staging area is not used.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PF62B5PJA2JDUOCKJGUQO3SPL74BEYSV/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WHIKB4TP6KBJWT2UIPWL5MWMG5QXKGEJ/
- https://www.debian.org/security/2018/dsa-4321
- http://www.securityfocus.com/bid/102981
- https://lists.debian.org/debian-lts-announce/2018/02/msg00017.html
- https://lists.debian.org/debian-lts-announce/2018/08/msg00002.html
- http://hg.graphicsmagick.org/hg/GraphicsMagick/rev/b41e2efce6d3
