# [M] CVE-2018-16749

## Summary
Severity: Medium
Advisory: CVE-2018-16749
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-09-09
Source: https://osv.dev/vulnerability/CVE-2018-16749
Type: osv

## Details
In ImageMagick 7.0.7-29 and earlier, a missing NULL check in ReadOneJNGImage in coders/png.c allows an attacker to cause a denial of service (WriteBlob assertion failure and application exit) via a crafted file.

## References
- https://lists.debian.org/debian-lts-announce/2018/10/msg00002.html
- https://lists.debian.org/debian-lts-announce/2020/09/msg00007.html
- https://usn.ubuntu.com/3785-1/
- https://github.com/ImageMagick/ImageMagick/issues/1119
- https://github.com/ImageMagick/ImageMagick6/commit/1007b98f8795ad4bea6bc5f68a32d83e982fdae4
