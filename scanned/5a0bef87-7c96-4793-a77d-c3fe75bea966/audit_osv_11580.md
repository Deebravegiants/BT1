# [M] CVE-2017-8830

## Summary
Severity: Medium
Advisory: CVE-2017-8830
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-05-08
Source: https://osv.dev/vulnerability/CVE-2017-8830
Type: osv

## Details
In ImageMagick 7.0.5-6, the ReadBMPImage function in bmp.c:1379 allows attackers to cause a denial of service (memory leak) via a crafted file.

## References
- http://www.securityfocus.com/bid/98687
- http://www.debian.org/security/2017/dsa-3863
- https://github.com/ImageMagick/ImageMagick/issues/467
