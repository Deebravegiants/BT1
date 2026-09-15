# [M] CVE-2017-11140

## Summary
Severity: Medium
Advisory: CVE-2017-11140
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-07-10
Source: https://osv.dev/vulnerability/CVE-2017-11140
Type: osv

## Details
The ReadJPEGImage function in coders/jpeg.c in GraphicsMagick 1.3.26 creates a pixel cache before a successful read of a scanline, which allows remote attackers to cause a denial of service (resource consumption) via crafted JPEG files.

## References
- https://lists.debian.org/debian-lts-announce/2018/08/msg00002.html
- https://usn.ubuntu.com/4206-1/
- http://www.securityfocus.com/bid/99503
- https://www.debian.org/security/2018/dsa-4321
- http://hg.code.sf.net/p/graphicsmagick/code/rev/b4139088b49a
