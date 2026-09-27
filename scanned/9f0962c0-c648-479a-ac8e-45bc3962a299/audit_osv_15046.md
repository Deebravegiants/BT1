# [M] CVE-2019-13108

## Summary
Severity: Medium
Advisory: CVE-2019-13108
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-06-30
Source: https://osv.dev/vulnerability/CVE-2019-13108
Type: osv

## Details
An integer overflow in Exiv2 through 0.27.1 allows an attacker to cause a denial of service (SIGSEGV) via a crafted PNG image file, because PngImage::readMetadata mishandles a zero value for iccOffset.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FGBT5OD2TF4AIXJUC56WOUJRHAZLZ4DC/
- https://github.com/Exiv2/exiv2/pull/794
- https://github.com/Exiv2/exiv2/issues/789
