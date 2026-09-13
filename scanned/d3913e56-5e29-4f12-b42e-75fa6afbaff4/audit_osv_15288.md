# [M] CVE-2019-14982

## Summary
Severity: Medium
Advisory: CVE-2019-14982
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-08-12
Source: https://osv.dev/vulnerability/CVE-2019-14982
Type: osv

## Details
In Exiv2 before v0.27.2, there is an integer overflow vulnerability in the WebPImage::getHeaderOffset function in webpimage.cpp. It can lead to a buffer overflow vulnerability and a crash.

## References
- https://github.com/Exiv2/exiv2/compare/v0.27.2-RC2...v0.27.2
- https://github.com/Exiv2/exiv2/issues/960
- https://github.com/Exiv2/exiv2/pull/962/commits/e925bc5addd881543fa503470c8a859e112cca62
