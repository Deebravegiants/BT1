# [M] CVE-2019-13111

## Summary
Severity: Medium
Advisory: CVE-2019-13111
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-06-30
Source: https://osv.dev/vulnerability/CVE-2019-13111
Type: osv

## Details
A WebPImage::decodeChunks integer overflow in Exiv2 through 0.27.1 allows an attacker to cause a denial of service (large heap allocation followed by a very long running loop) via a crafted WEBP image file.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FGBT5OD2TF4AIXJUC56WOUJRHAZLZ4DC/
- https://github.com/Exiv2/exiv2/issues/791
- https://github.com/Exiv2/exiv2/pull/797
