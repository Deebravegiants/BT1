# [M] CVE-2017-11536

## Summary
Severity: Medium
Advisory: CVE-2017-11536
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2017-07-23
Source: https://osv.dev/vulnerability/CVE-2017-11536
Type: osv

## Details
When ImageMagick 7.0.6-1 processes a crafted file in convert, it can lead to a Memory Leak in the WriteJP2Image() function in coders/jp2.c.

## References
- http://www.securityfocus.com/bid/100000
- https://github.com/ImageMagick/ImageMagick/issues/567
