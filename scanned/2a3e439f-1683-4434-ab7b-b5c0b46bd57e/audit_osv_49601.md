# [M] CVE-2019-14369

## Summary
Severity: Medium
Advisory: CVE-2019-14369
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-07-28
Source: https://osv.dev/vulnerability/CVE-2019-14369
Type: osv

## Details
Exiv2::PngImage::readMetadata() in pngimage.cpp in Exiv2 0.27.99.0 allows attackers to cause a denial of service (heap-based buffer over-read) via a crafted image file.

## References
- https://lists.debian.org/debian-lts-announce/2023/01/msg00004.html
- https://github.com/Exiv2/exiv2/issues/953
