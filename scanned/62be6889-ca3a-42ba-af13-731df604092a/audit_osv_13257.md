# [M] CVE-2018-18915

## Summary
Severity: Medium
Advisory: CVE-2018-18915
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-11-03
Source: https://osv.dev/vulnerability/CVE-2018-18915
Type: osv

## Details
There is an infinite loop in the Exiv2::Image::printIFDStructure function of image.cpp in Exiv2 0.27-RC1. A crafted input will lead to a remote denial of service attack.

## References
- https://access.redhat.com/errata/RHSA-2019:2101
- https://github.com/Exiv2/exiv2/issues/511
