# [M] CVE-2018-18023

## Summary
Severity: Medium
Advisory: CVE-2018-18023
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-10-07
Source: https://osv.dev/vulnerability/CVE-2018-18023
Type: osv

## Details
In ImageMagick 7.0.8-13 Q16, there is a heap-based buffer over-read in the SVGStripString function of coders/svg.c, which allows attackers to cause a denial of service via a crafted SVG image file.

## References
- https://usn.ubuntu.com/4034-1/
- https://github.com/ImageMagick/ImageMagick/issues/1336
