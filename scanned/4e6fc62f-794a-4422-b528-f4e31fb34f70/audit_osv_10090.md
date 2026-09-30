# [M] CVE-2017-13658

## Summary
Severity: Medium
Advisory: CVE-2017-13658
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-08-24
Source: https://osv.dev/vulnerability/CVE-2017-13658
Type: osv

## Details
In ImageMagick before 6.9.9-3 and 7.x before 7.0.6-3, there is a missing NULL check in the ReadMATImage function in coders/mat.c, leading to a denial of service (assertion failure and application exit) in the DestroyImageInfo function in MagickCore/image.c.

## References
- https://lists.debian.org/debian-lts-announce/2019/05/msg00015.html
- https://lists.debian.org/debian-lts-announce/2020/09/msg00007.html
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=870019
- https://github.com/ImageMagick/ImageMagick/commit/e5c063a1007506ba69e97a35effcdef944421c89
- https://github.com/ImageMagick/ImageMagick/issues/598
