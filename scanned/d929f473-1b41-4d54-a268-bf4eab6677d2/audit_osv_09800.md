# [M] CVE-2017-11533

## Summary
Severity: Medium
Advisory: CVE-2017-11533
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-07-23
Source: https://osv.dev/vulnerability/CVE-2017-11533
Type: osv

## Details
When ImageMagick 7.0.6-1 processes a crafted file in convert, it can lead to a heap-based buffer over-read in the WriteUILImage() function in coders/uil.c.

## References
- https://usn.ubuntu.com/3681-1/
- https://www.debian.org/security/2017/dsa-4019
- https://www.debian.org/security/2018/dsa-4204
- https://github.com/ImageMagick/ImageMagick/issues/562
