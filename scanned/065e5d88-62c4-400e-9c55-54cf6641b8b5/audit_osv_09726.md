# [M] CVE-2017-11141

## Summary
Severity: Medium
Advisory: CVE-2017-11141
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-07-10
Source: https://osv.dev/vulnerability/CVE-2017-11141
Type: osv

## Details
The ReadMATImage function in coders\mat.c in ImageMagick 7.0.5-6 has a memory leak vulnerability that can cause memory exhaustion via a crafted MAT file, related to incorrect ordering of a SetImageExtent call.

## References
- http://www.securityfocus.com/bid/99506
- https://github.com/ImageMagick/ImageMagick/issues/469
