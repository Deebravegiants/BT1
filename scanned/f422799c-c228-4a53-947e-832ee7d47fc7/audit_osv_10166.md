# [H] CVE-2017-14137

## Summary
Severity: High
Advisory: CVE-2017-14137
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-09-04
Source: https://osv.dev/vulnerability/CVE-2017-14137
Type: osv

## Details
ReadWEBPImage in coders/webp.c in ImageMagick 7.0.6-5 has an issue where memory allocation is excessive because it depends only on a length field in a header.

## References
- https://security.gentoo.org/glsa/201711-07
- https://github.com/ImageMagick/ImageMagick/issues/641
