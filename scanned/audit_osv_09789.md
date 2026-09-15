# [M] CVE-2017-11522

## Summary
Severity: Medium
Advisory: CVE-2017-11522
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-07-22
Source: https://osv.dev/vulnerability/CVE-2017-11522
Type: osv

## Details
The WriteOnePNGImage function in coders/png.c in ImageMagick through 6.9.9-0 and 7.x through 7.0.6-1 allows remote attackers to cause a denial of service (NULL pointer dereference) via a crafted file.

## References
- https://bugs.debian.org/869209
- https://github.com/ImageMagick/ImageMagick/commit/816ecab6c532ae086ff4186b3eaf4aa7092d536f
- https://github.com/ImageMagick/ImageMagick/issues/586
