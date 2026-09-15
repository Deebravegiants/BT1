# [C] CVE-2017-11643

## Summary
Severity: Critical
Advisory: CVE-2017-11643
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-07-26
Source: https://osv.dev/vulnerability/CVE-2017-11643
Type: osv

## Details
GraphicsMagick 1.3.26 has a heap overflow in the WriteCMYKImage() function in coders/cmyk.c when processing multiple frames that have non-identical widths.

## References
- http://www.securityfocus.com/bid/100357
- https://lists.debian.org/debian-lts-announce/2018/06/msg00009.html
- https://usn.ubuntu.com/4222-1/
- http://hg.code.sf.net/p/graphicsmagick/code/rev/d00b74315a71
- https://www.debian.org/security/2018/dsa-4321
