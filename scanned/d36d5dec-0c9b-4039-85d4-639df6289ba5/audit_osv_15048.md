# [M] CVE-2019-13110

## Summary
Severity: Medium
Advisory: CVE-2019-13110
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-06-30
Source: https://osv.dev/vulnerability/CVE-2019-13110
Type: osv

## Details
A CiffDirectory::readDirectory integer overflow and out-of-bounds read in Exiv2 through 0.27.1 allows an attacker to cause a denial of service (SIGSEGV) via a crafted CRW image file.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FGBT5OD2TF4AIXJUC56WOUJRHAZLZ4DC/
- https://lists.debian.org/debian-lts-announce/2023/01/msg00004.html
- https://usn.ubuntu.com/4056-1/
- https://github.com/Exiv2/exiv2/pull/844
- https://github.com/Exiv2/exiv2/issues/843
