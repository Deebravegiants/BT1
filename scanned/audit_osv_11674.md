# [M] CVE-2017-9262

## Summary
Severity: Medium
Advisory: CVE-2017-9262
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-05-29
Source: https://osv.dev/vulnerability/CVE-2017-9262
Type: osv

## Details
In ImageMagick 7.0.5-6 Q16, the ReadJNGImage function in coders/png.c allows attackers to cause a denial of service (memory leak) via a crafted file.

## References
- http://www.securityfocus.com/bid/98735
- https://github.com/ImageMagick/ImageMagick/issues/475
