# [M] CVE-2017-14249

## Summary
Severity: Medium
Advisory: CVE-2017-14249
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-09-11
Source: https://osv.dev/vulnerability/CVE-2017-14249
Type: osv

## Details
ImageMagick 7.0.6-8 Q16 mishandles EOF checks in ReadMPCImage in coders/mpc.c, leading to division by zero in GetPixelCacheTileSize in MagickCore/cache.c, allowing remote attackers to cause a denial of service via a crafted file.

## References
- https://lists.debian.org/debian-lts-announce/2019/05/msg00015.html
- https://lists.debian.org/debian-lts-announce/2020/09/msg00007.html
- https://usn.ubuntu.com/3681-1/
- https://security.gentoo.org/glsa/201711-07
- https://github.com/ImageMagick/ImageMagick/issues/708
