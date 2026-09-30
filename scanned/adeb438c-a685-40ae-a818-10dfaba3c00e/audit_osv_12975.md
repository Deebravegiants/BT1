# [M] CVE-2018-16643

## Summary
Severity: Medium
Advisory: CVE-2018-16643
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-09-06
Source: https://osv.dev/vulnerability/CVE-2018-16643
Type: osv

## Details
The functions ReadDCMImage in coders/dcm.c, ReadPWPImage in coders/pwp.c, ReadCALSImage in coders/cals.c, and ReadPICTImage in coders/pict.c in ImageMagick 7.0.8-4 do not check the return value of the fputc function, which allows remote attackers to cause a denial of service via a crafted image file.

## References
- https://lists.debian.org/debian-lts-announce/2020/09/msg00007.html
- https://lists.debian.org/debian-lts-announce/2018/10/msg00002.html
- https://usn.ubuntu.com/3785-1/
- https://github.com/ImageMagick/ImageMagick/commit/6b6bff054d569a77973f2140c0e86366e6168a6c
- https://github.com/ImageMagick/ImageMagick/issues/1199
