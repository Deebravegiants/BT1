# [H] CVE-2017-16669

## Summary
Severity: High
Advisory: CVE-2017-16669
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-11-09
Source: https://osv.dev/vulnerability/CVE-2017-16669
Type: osv

## Details
coders/wpg.c in GraphicsMagick 1.3.26 allows remote attackers to cause a denial of service (heap-based buffer overflow and application crash) or possibly have unspecified other impact via a crafted file, related to the AcquireCacheNexus function in magick/pixel_cache.c.

## References
- https://usn.ubuntu.com/4248-1/
- https://lists.debian.org/debian-lts-announce/2018/06/msg00009.html
- https://www.debian.org/security/2018/dsa-4321
- http://www.securityfocus.com/bid/101795
- https://lists.debian.org/debian-lts-announce/2017/11/msg00013.html
- http://hg.code.sf.net/p/graphicsmagick/code/rev/135bdcb88b8d
- http://hg.code.sf.net/p/graphicsmagick/code/rev/3dc7b4e3779d
- http://hg.code.sf.net/p/graphicsmagick/code/rev/e8086faa52d0
- https://sourceforge.net/p/graphicsmagick/bugs/450/
- http://hg.code.sf.net/p/graphicsmagick/code/rev/1b9e64a8901e
- http://hg.code.sf.net/p/graphicsmagick/code/rev/2a21cda3145b
- http://hg.code.sf.net/p/graphicsmagick/code/rev/2b7c826d36af
- http://hg.code.sf.net/p/graphicsmagick/code/rev/75245a215fff
- http://hg.code.sf.net/p/graphicsmagick/code/rev/fcd3ed3394f6
