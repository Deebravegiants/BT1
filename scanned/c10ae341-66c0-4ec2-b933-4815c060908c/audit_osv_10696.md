# [M] CVE-2017-18271

## Summary
Severity: Medium
Advisory: CVE-2017-18271
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-05-18
Source: https://osv.dev/vulnerability/CVE-2017-18271
Type: osv

## Details
In ImageMagick 7.0.7-16 Q16 x86_64 2017-12-22, an infinite loop vulnerability was found in the function ReadMIFFImage in coders/miff.c, which allows attackers to cause a denial of service (CPU exhaustion) via a crafted MIFF image file.

## References
- https://lists.debian.org/debian-lts-announce/2019/05/msg00015.html
- https://lists.debian.org/debian-lts-announce/2020/09/msg00007.html
- https://github.com/ImageMagick/ImageMagick/issues/911
- https://lists.debian.org/debian-lts-announce/2018/05/msg00012.html
- https://usn.ubuntu.com/3681-1/
