# [M] CVE-2018-16642

## Summary
Severity: Medium
Advisory: CVE-2018-16642
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-09-06
Source: https://osv.dev/vulnerability/CVE-2018-16642
Type: osv

## Details
The function InsertRow in coders/cut.c in ImageMagick 7.0.7-37 allows remote attackers to cause a denial of service via a crafted image file due to an out-of-bounds write.

## References
- https://lists.debian.org/debian-lts-announce/2018/10/msg00002.html
- https://usn.ubuntu.com/3785-1/
- https://www.debian.org/security/2018/dsa-4316
- https://github.com/ImageMagick/ImageMagick/commit/cc4ac341f29fa368da6ef01c207deaf8c61f6a2e
- https://github.com/ImageMagick/ImageMagick/issues/1162
