# [C] CVE-2017-11637

## Summary
Severity: Critical
Advisory: CVE-2017-11637
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-07-26
Source: https://osv.dev/vulnerability/CVE-2017-11637
Type: osv

## Details
GraphicsMagick 1.3.26 has a NULL pointer dereference in the WritePCLImage() function in coders/pcl.c during writes of monochrome images.

## References
- https://lists.debian.org/debian-lts-announce/2018/08/msg00002.html
- https://usn.ubuntu.com/4206-1/
- http://hg.code.sf.net/p/graphicsmagick/code/rev/f3ffc5541257
- https://www.debian.org/security/2018/dsa-4321
