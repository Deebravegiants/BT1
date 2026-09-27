# [M] CVE-2018-16645

## Summary
Severity: Medium
Advisory: CVE-2018-16645
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-09-06
Source: https://osv.dev/vulnerability/CVE-2018-16645
Type: osv

## Details
There is an excessive memory allocation issue in the functions ReadBMPImage of coders/bmp.c and ReadDIBImage of coders/dib.c in ImageMagick 7.0.8-11, which allows remote attackers to cause a denial of service via a crafted image file.

## References
- https://usn.ubuntu.com/4034-1/
- https://lists.debian.org/debian-lts-announce/2018/10/msg00002.html
- https://usn.ubuntu.com/3785-1/
- https://www.debian.org/security/2018/dsa-4316
- https://github.com/ImageMagick/ImageMagick/commit/ecb31dbad39ccdc65868d5d2a37f0f0521250832
- https://github.com/ImageMagick/ImageMagick/issues/1268
