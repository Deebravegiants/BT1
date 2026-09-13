# [M] CVE-2017-9142

## Summary
Severity: Medium
Advisory: CVE-2017-9142
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-05-22
Source: https://osv.dev/vulnerability/CVE-2017-9142
Type: osv

## Details
In ImageMagick 7.0.5-7 Q16, a crafted file could trigger an assertion failure in the WriteBlob function in MagickCore/blob.c because of missing checks in the ReadOneJNGImage function in coders/png.c.

## References
- http://www.debian.org/security/2017/dsa-3863
- http://www.securityfocus.com/bid/98683
- https://github.com/ImageMagick/ImageMagick/commit/f0232a2a45dfd003c1faf6079497895df3ab0ee1
- https://github.com/ImageMagick/ImageMagick/issues/490
