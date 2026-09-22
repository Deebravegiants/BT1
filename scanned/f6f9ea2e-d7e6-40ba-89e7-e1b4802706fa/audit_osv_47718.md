# [M] CVE-2017-10799

## Summary
Severity: Medium
Advisory: CVE-2017-10799
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-07-03
Source: https://osv.dev/vulnerability/CVE-2017-10799
Type: osv

## Details
When GraphicsMagick 1.3.25 processes a DPX image (with metadata indicating a large width) in coders/dpx.c, a denial of service (OOM) can occur in ReadDPXImage().

## References
- https://lists.debian.org/debian-lts-announce/2019/04/msg00015.html
- https://usn.ubuntu.com/4206-1/
- https://www.debian.org/security/2018/dsa-4321
- http://www.securityfocus.com/bid/99358
- http://hg.code.sf.net/p/graphicsmagick/code/rev/f10b9bb3ca62
