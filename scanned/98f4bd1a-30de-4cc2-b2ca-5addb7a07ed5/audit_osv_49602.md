# [M] CVE-2019-14370

## Summary
Severity: Medium
Advisory: CVE-2019-14370
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-07-28
Source: https://osv.dev/vulnerability/CVE-2019-14370
Type: osv

## Details
In Exiv2 0.27.99.0, there is an out-of-bounds read in Exiv2::MrwImage::readMetadata() in mrwimage.cpp. It could result in denial of service.

## References
- https://lists.debian.org/debian-lts-announce/2023/01/msg00004.html
- https://github.com/Exiv2/exiv2/issues/954
