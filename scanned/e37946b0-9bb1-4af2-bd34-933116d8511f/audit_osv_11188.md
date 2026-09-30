# [M] CVE-2017-6502

## Summary
Severity: Medium
Advisory: CVE-2017-6502
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-03-06
Source: https://osv.dev/vulnerability/CVE-2017-6502
Type: osv

## Details
An issue was discovered in ImageMagick 6.9.7. A specially crafted webp file could lead to a file-descriptor leak in libmagickcore (thus, a DoS).

## References
- http://www.securityfocus.com/bid/96763
- https://github.com/ImageMagick/ImageMagick/commit/126c7c98ea788241922c30df4a5633ea692cf8df
