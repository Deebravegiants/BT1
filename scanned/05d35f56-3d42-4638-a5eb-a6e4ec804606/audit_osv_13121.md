# [M] CVE-2018-17581

## Summary
Severity: Medium
Advisory: CVE-2018-17581
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-09-28
Source: https://osv.dev/vulnerability/CVE-2018-17581
Type: osv

## Details
CiffDirectory::readDirectory() at crwimage_int.cpp in Exiv2 0.26 has excessive stack consumption due to a recursive function, leading to Denial of service.

## References
- https://access.redhat.com/errata/RHSA-2019:2101
- https://lists.debian.org/debian-lts-announce/2019/02/msg00038.html
- https://lists.debian.org/debian-lts-announce/2023/01/msg00004.html
- https://usn.ubuntu.com/3852-1/
- https://github.com/Exiv2/exiv2/issues/460
- https://github.com/SegfaultMasters/covering360/blob/master/Exiv2
