# [C] CVE-2018-14551

## Summary
Severity: Critical
Advisory: CVE-2018-14551
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-07-23
Source: https://osv.dev/vulnerability/CVE-2018-14551
Type: osv

## Details
The ReadMATImageV4 function in coders/mat.c in ImageMagick 7.0.8-7 uses an uninitialized variable, leading to memory corruption.

## References
- https://lists.debian.org/debian-lts-announce/2020/08/msg00030.html
- https://usn.ubuntu.com/3785-1/
- https://github.com/ImageMagick/ImageMagick/issues/1221
