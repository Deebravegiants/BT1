# [M] CVE-2019-14980

## Summary
Severity: Medium
Advisory: CVE-2019-14980
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-08-12
Source: https://osv.dev/vulnerability/CVE-2019-14980
Type: osv

## Details
In ImageMagick 7.x before 7.0.8-42 and 6.x before 6.9.10-42, there is a use after free vulnerability in the UnmapBlob function that allows an attacker to cause a denial of service by sending a crafted file.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-11/msg00040.html
- http://lists.opensuse.org/opensuse-security-announce/2019-11/msg00042.html
- https://github.com/ImageMagick/ImageMagick6/issues/43
- https://github.com/ImageMagick/ImageMagick/commit/c5d012a46ae22be9444326aa37969a3f75daa3ba
- https://github.com/ImageMagick/ImageMagick/compare/7.0.8-41...7.0.8-42
- https://github.com/ImageMagick/ImageMagick6/commit/614a257295bdcdeda347086761062ac7658b6830
