# [M] CVE-2018-5358

## Summary
Severity: Medium
Advisory: CVE-2018-5358
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-01-12
Source: https://osv.dev/vulnerability/CVE-2018-5358
Type: osv

## Details
ImageMagick 7.0.7-22 Q16 has memory leaks in the EncodeImageAttributes function in coders/json.c, as demonstrated by the ReadPSDLayersInternal function in coders/psd.c.

## References
- https://usn.ubuntu.com/3681-1/
- https://github.com/ImageMagick/ImageMagick/issues/939
