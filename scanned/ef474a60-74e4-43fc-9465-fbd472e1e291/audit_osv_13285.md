# [M] CVE-2018-19108

## Summary
Severity: Medium
Advisory: CVE-2018-19108
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-11-08
Source: https://osv.dev/vulnerability/CVE-2018-19108
Type: osv

## Details
In Exiv2 0.26, Exiv2::PsdImage::readMetadata in psdimage.cpp in the PSD image reader may suffer from a denial of service (infinite loop) caused by an integer overflow via a crafted PSD image file.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-04/msg00009.html
- https://access.redhat.com/errata/RHSA-2019:2101
- https://lists.debian.org/debian-lts-announce/2019/02/msg00038.html
- https://lists.debian.org/debian-lts-announce/2023/01/msg00004.html
- https://usn.ubuntu.com/4056-1/
- https://github.com/Exiv2/exiv2/issues/426
- https://github.com/Exiv2/exiv2/pull/518
