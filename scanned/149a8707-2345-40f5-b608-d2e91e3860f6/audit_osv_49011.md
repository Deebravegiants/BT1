# [M] CVE-2018-20189

## Summary
Severity: Medium
Advisory: CVE-2018-20189
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-12-17
Source: https://osv.dev/vulnerability/CVE-2018-20189
Type: osv

## Details
In GraphicsMagick 1.3.31, the ReadDIBImage function of coders/dib.c has a vulnerability allowing a crash and denial of service via a dib file that is crafted to appear with direct pixel values and also colormapping (which is not available beyond 8-bits/sample), and therefore lacks indexes initialization.

## References
- https://usn.ubuntu.com/4207-1/
- http://www.securityfocus.com/bid/106227
- https://lists.debian.org/debian-lts-announce/2018/12/msg00018.html
- https://www.debian.org/security/2020/dsa-4640
- http://hg.graphicsmagick.org/hg/GraphicsMagick/rev/648e2b406589
- https://sourceforge.net/p/graphicsmagick/bugs/585/
