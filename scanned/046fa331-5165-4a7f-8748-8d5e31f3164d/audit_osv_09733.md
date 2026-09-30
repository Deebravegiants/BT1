# [M] CVE-2017-11166

## Summary
Severity: Medium
Advisory: CVE-2017-11166
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-07-10
Source: https://osv.dev/vulnerability/CVE-2017-11166
Type: osv

## Details
The ReadXWDImage function in coders\xwd.c in ImageMagick 7.0.5-6 has a memory leak vulnerability that can cause memory exhaustion via a crafted length (number of color-map entries) field in the header of an XWD file.

## References
- https://github.com/ImageMagick/ImageMagick/issues/471
