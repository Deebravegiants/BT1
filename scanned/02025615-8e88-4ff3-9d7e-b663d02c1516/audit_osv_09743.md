# [H] CVE-2017-11310

## Summary
Severity: High
Advisory: CVE-2017-11310
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-07-13
Source: https://osv.dev/vulnerability/CVE-2017-11310
Type: osv

## Details
The read_user_chunk_callback function in coders\png.c in ImageMagick 7.0.6-1 Q16 2017-06-21 (beta) has memory leak vulnerabilities via crafted PNG files.

## References
- http://www.securityfocus.com/bid/99585
- https://github.com/ImageMagick/ImageMagick/commit/8ca35831e91c3db8c6d281d09b605001003bec08
- https://github.com/ImageMagick/ImageMagick/issues/517
