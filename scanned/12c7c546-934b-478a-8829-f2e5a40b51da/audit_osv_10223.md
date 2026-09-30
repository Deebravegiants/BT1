# [M] CVE-2017-14400

## Summary
Severity: Medium
Advisory: CVE-2017-14400
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-09-12
Source: https://osv.dev/vulnerability/CVE-2017-14400
Type: osv

## Details
In ImageMagick 7.0.7-1 Q16, the PersistPixelCache function in magick/cache.c mishandles the pixel cache nexus, which allows remote attackers to cause a denial of service (NULL pointer dereference in the function GetVirtualPixels in MagickCore/cache.c) via a crafted file.

## References
- https://lists.debian.org/debian-lts-announce/2019/05/msg00015.html
- https://lists.debian.org/debian-lts-announce/2020/09/msg00007.html
- https://usn.ubuntu.com/3681-1/
- http://www.securityfocus.com/bid/100865
- https://github.com/ImageMagick/ImageMagick/issues/746
