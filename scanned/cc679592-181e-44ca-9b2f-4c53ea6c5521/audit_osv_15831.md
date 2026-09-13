# [C] CVE-2019-19952

## Summary
Severity: Critical
Advisory: CVE-2019-19952
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-12-24
Source: https://osv.dev/vulnerability/CVE-2019-19952
Type: osv

## Details
In ImageMagick 7.0.9-7 Q16, there is a use-after-free in the function MngInfoDiscardObject of coders/png.c, related to ReadOneMNGImage.

## References
- https://github.com/ImageMagick/ImageMagick/issues/1791
