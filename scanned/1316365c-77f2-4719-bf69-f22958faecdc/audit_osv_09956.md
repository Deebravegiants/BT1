# [M] CVE-2017-12434

## Summary
Severity: Medium
Advisory: CVE-2017-12434
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-08-04
Source: https://osv.dev/vulnerability/CVE-2017-12434
Type: osv

## Details
In ImageMagick 7.0.6-1, a missing NULL check vulnerability was found in the function ReadMATImage in coders/mat.c, which allows attackers to cause a denial of service (assertion failure) in DestroyImageInfo in image.c.

## References
- https://www.debian.org/security/2017/dsa-4019
- https://github.com/ImageMagick/ImageMagick/issues/547
