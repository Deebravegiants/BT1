# [H] CVE-2018-12264

## Summary
Severity: High
Advisory: CVE-2018-12264
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-06-13
Source: https://osv.dev/vulnerability/CVE-2018-12264
Type: osv

## Details
Exiv2 0.26 has integer overflows in LoaderTiff::getData() in preview.cpp, leading to an out-of-bounds read in Exiv2::ValueType::setDataArea in value.hpp.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-04/msg00009.html
- https://access.redhat.com/errata/RHSA-2019:2101
- https://lists.debian.org/debian-lts-announce/2018/06/msg00010.html
- https://security.gentoo.org/glsa/201811-14
- https://usn.ubuntu.com/3700-1/
- https://www.debian.org/security/2018/dsa-4238
- https://github.com/Exiv2/exiv2/issues/366
- https://github.com/TeamSeri0us/pocs/blob/master/exiv2/2-out-of-read-Poc
