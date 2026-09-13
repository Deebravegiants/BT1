# [M] CVE-2018-8976

## Summary
Severity: Medium
Advisory: CVE-2018-8976
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-03-25
Source: https://osv.dev/vulnerability/CVE-2018-8976
Type: osv

## Details
In Exiv2 0.26, jpgimage.cpp allows remote attackers to cause a denial of service (image.cpp Exiv2::Internal::stringFormat out-of-bounds read) via a crafted file.

## References
- https://access.redhat.com/errata/RHSA-2019:2101
- https://lists.debian.org/debian-lts-announce/2023/01/msg00004.html
- https://security.gentoo.org/glsa/201811-14
- https://github.com/Exiv2/exiv2/issues/246
