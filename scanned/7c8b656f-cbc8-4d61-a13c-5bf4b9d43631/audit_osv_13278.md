# [M] CVE-2018-19058

## Summary
Severity: Medium
Advisory: CVE-2018-19058
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-11-07
Source: https://osv.dev/vulnerability/CVE-2018-19058
Type: osv

## Details
An issue was discovered in Poppler 0.71.0. There is a reachable abort in Object.h, will lead to denial of service because EmbFile::save2 in FileSpec.cc lacks a stream check before saving an embedded file.

## References
- https://access.redhat.com/errata/RHSA-2019:2022
- https://lists.debian.org/debian-lts-announce/2019/03/msg00008.html
- https://lists.debian.org/debian-lts-announce/2020/11/msg00014.html
- https://lists.debian.org/debian-lts-announce/2022/09/msg00030.html
- https://usn.ubuntu.com/3837-1/
- https://gitlab.freedesktop.org/poppler/poppler/issues/659
