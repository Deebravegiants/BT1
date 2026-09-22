# [C] CVE-2017-14138

## Summary
Severity: Critical
Advisory: CVE-2017-14138
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-09-04
Source: https://osv.dev/vulnerability/CVE-2017-14138
Type: osv

## Details
ImageMagick 7.0.6-5 has a memory leak vulnerability in ReadWEBPImage in coders/webp.c because memory is not freed in certain error cases, as demonstrated by VP8 errors.

## References
- https://security.gentoo.org/glsa/201711-07
- https://github.com/ImageMagick/ImageMagick/issues/639
