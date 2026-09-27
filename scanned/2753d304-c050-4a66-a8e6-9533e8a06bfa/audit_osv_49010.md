# [M] CVE-2018-20185

## Summary
Severity: Medium
Advisory: CVE-2018-20185
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-12-17
Source: https://osv.dev/vulnerability/CVE-2018-20185
Type: osv

## Details
In GraphicsMagick 1.4 snapshot-20181209 Q8 on 32-bit platforms, there is a heap-based buffer over-read in the ReadBMPImage function of bmp.c, which allows attackers to cause a denial of service via a crafted bmp image file. This only affects GraphicsMagick installations with customized BMP limits.

## References
- https://usn.ubuntu.com/4207-1/
- https://www.debian.org/security/2020/dsa-4640
- http://www.securityfocus.com/bid/106229
- https://lists.debian.org/debian-lts-announce/2018/12/msg00018.html
- http://hg.graphicsmagick.org/hg/GraphicsMagick/rev/648e3977a293
- https://sourceforge.net/p/graphicsmagick/bugs/582/
