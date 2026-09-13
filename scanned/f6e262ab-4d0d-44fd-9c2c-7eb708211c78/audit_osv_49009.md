# [M] CVE-2018-20184

## Summary
Severity: Medium
Advisory: CVE-2018-20184
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-12-17
Source: https://osv.dev/vulnerability/CVE-2018-20184
Type: osv

## Details
In GraphicsMagick 1.4 snapshot-20181209 Q8, there is a heap-based buffer overflow in the WriteTGAImage function of tga.c, which allows attackers to cause a denial of service via a crafted image file, because the number of rows or columns can exceed the pixel-dimension restrictions of the TGA specification.

## References
- https://usn.ubuntu.com/4207-1/
- https://www.debian.org/security/2020/dsa-4640
- http://www.securityfocus.com/bid/106229
- https://lists.debian.org/debian-lts-announce/2018/12/msg00018.html
- http://hg.graphicsmagick.org/hg/GraphicsMagick/rev/15d1b5fd003b
- https://sourceforge.net/p/graphicsmagick/bugs/583/
