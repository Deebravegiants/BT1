# [M] CVE-2017-17883

## Summary
Severity: Medium
Advisory: CVE-2017-17883
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-12-27
Source: https://osv.dev/vulnerability/CVE-2017-17883
Type: osv

## Details
In ImageMagick 7.0.7-12 Q16, a memory leak vulnerability was found in the function ReadPGXImage in coders/pgx.c, which allows attackers to cause a denial of service via a crafted PGX image file.

## References
- https://github.com/ImageMagick/ImageMagick/issues/877
