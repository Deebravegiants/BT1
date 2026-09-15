# [M] CVE-2018-20650

## Summary
Severity: Medium
Advisory: CVE-2018-20650
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-01-01
Source: https://osv.dev/vulnerability/CVE-2018-20650
Type: osv

## Details
A reachable Object::dictLookup assertion in Poppler 0.72.0 allows attackers to cause a denial of service due to the lack of a check for the dict data type, as demonstrated by use of the FileSpec class (in FileSpec.cc) in pdfdetach.

## References
- http://www.securityfocus.com/bid/106459
- https://access.redhat.com/errata/RHSA-2019:2022
- https://access.redhat.com/errata/RHSA-2019:2713
- https://lists.debian.org/debian-lts-announce/2019/09/msg00033.html
- https://lists.debian.org/debian-lts-announce/2020/11/msg00014.html
- https://lists.debian.org/debian-lts-announce/2022/09/msg00030.html
- https://usn.ubuntu.com/3865-1/
- https://gitlab.freedesktop.org/poppler/poppler/commit/de0c0b8324e776f0b851485e0fc9622fc35695b7
- https://gitlab.freedesktop.org/poppler/poppler/issues/704
