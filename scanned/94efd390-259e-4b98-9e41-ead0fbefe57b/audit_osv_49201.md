# [M] CVE-2018-5685

## Summary
Severity: Medium
Advisory: CVE-2018-5685
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-01-14
Source: https://osv.dev/vulnerability/CVE-2018-5685
Type: osv

## Details
In GraphicsMagick 1.3.27, there is an infinite loop and application hang in the ReadBMPImage function (coders/bmp.c). Remote attackers could leverage this vulnerability to cause a denial of service via an image file with a crafted bit-field mask value.

## References
- https://lists.debian.org/debian-lts-announce/2018/01/msg00018.html
- https://lists.debian.org/debian-lts-announce/2018/08/msg00002.html
- https://www.debian.org/security/2018/dsa-4321
- https://sourceforge.net/p/graphicsmagick/bugs/541/
- http://hg.graphicsmagick.org/hg/GraphicsMagick/rev/52a91ddb1aa6
