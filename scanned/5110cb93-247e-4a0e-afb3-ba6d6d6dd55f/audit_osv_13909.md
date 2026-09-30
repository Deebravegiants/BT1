# [H] CVE-2018-5248

## Summary
Severity: High
Advisory: CVE-2018-5248
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-01-05
Source: https://osv.dev/vulnerability/CVE-2018-5248
Type: osv

## Details
In ImageMagick 7.0.7-17 Q16, there is a heap-based buffer over-read in coders/sixel.c in the ReadSIXELImage function, related to the sixel_decode function.

## References
- http://www.securityfocus.com/bid/102431
- https://usn.ubuntu.com/3681-1/
- https://www.debian.org/security/2018/dsa-4204
- https://www.debian.org/security/2018/dsa-4245
- https://github.com/ImageMagick/ImageMagick/issues/927
