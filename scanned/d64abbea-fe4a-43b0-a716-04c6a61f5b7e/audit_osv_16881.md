# [M] CVE-2020-10251

## Summary
Severity: Medium
Advisory: CVE-2020-10251
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2020-03-10
Source: https://osv.dev/vulnerability/CVE-2020-10251
Type: osv

## Details
In ImageMagick 7.0.9, an out-of-bounds read vulnerability exists within the ReadHEICImageByID function in coders\heic.c. It can be triggered via an image with a width or height value that exceeds the actual size of the image.

## References
- https://github.com/ImageMagick/ImageMagick/issues/1859
