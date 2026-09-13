# [M] CVE-2018-10998

## Summary
Severity: Medium
Advisory: CVE-2018-10998
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-05-12
Source: https://osv.dev/vulnerability/CVE-2018-10998
Type: osv

## Details
An issue was discovered in Exiv2 0.26. readMetadata in jp2image.cpp allows remote attackers to cause a denial of service (SIGABRT) by triggering an incorrect Safe::add call.

## References
- https://access.redhat.com/errata/RHSA-2019:2101
- https://lists.debian.org/debian-lts-announce/2018/06/msg00010.html
- https://security.gentoo.org/glsa/201811-14
- https://usn.ubuntu.com/3700-1/
- https://www.debian.org/security/2018/dsa-4238
- https://github.com/Exiv2/exiv2/issues/303
