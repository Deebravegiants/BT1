# [M] CVE-2017-11534

## Summary
Severity: Medium
Advisory: CVE-2017-11534
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-07-23
Source: https://osv.dev/vulnerability/CVE-2017-11534
Type: osv

## Details
When ImageMagick 7.0.6-1 processes a crafted file in convert, it can lead to a Memory Leak in the lite_font_map() function in coders/wmf.c.

## References
- https://github.com/ImageMagick/ImageMagick/issues/564
