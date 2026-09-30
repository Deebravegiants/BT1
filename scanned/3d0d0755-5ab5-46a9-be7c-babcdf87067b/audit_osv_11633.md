# [M] CVE-2017-9143

## Summary
Severity: Medium
Advisory: CVE-2017-9143
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-05-22
Source: https://osv.dev/vulnerability/CVE-2017-9143
Type: osv

## Details
In ImageMagick 7.0.5-5, the ReadARTImage function in coders/art.c allows attackers to cause a denial of service (memory leak) via a crafted .art file.

## References
- http://www.debian.org/security/2017/dsa-3863
- http://www.securityfocus.com/bid/98682
- https://github.com/ImageMagick/ImageMagick/commit/3b0fe05cddd8910f84e51b4d50099702ea45ba4a
- https://github.com/ImageMagick/ImageMagick/issues/456
