# [M] CVE-2017-18231

## Summary
Severity: Medium
Advisory: CVE-2017-18231
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-03-14
Source: https://osv.dev/vulnerability/CVE-2017-18231
Type: osv

## Details
An issue was discovered in GraphicsMagick 1.3.26. A NULL pointer dereference vulnerability was found in the function ReadEnhMetaFile in coders/emf.c, which allows attackers to cause a denial of service via a crafted file.

## References
- https://usn.ubuntu.com/4266-1/
- https://www.debian.org/security/2018/dsa-4321
- https://lists.debian.org/debian-lts-announce/2018/03/msg00025.html
- https://lists.debian.org/debian-lts-announce/2018/08/msg00002.html
- https://sourceforge.net/p/graphicsmagick/bugs/475/
- http://hg.graphicsmagick.org/hg/GraphicsMagick/rev/ea074081678b
