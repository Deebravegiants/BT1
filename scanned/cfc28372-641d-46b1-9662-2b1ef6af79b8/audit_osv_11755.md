# [M] CVE-2017-9501

## Summary
Severity: Medium
Advisory: CVE-2017-9501
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-06-07
Source: https://osv.dev/vulnerability/CVE-2017-9501
Type: osv

## Details
In ImageMagick 7.0.5-7 Q16, an assertion failure was found in the function LockSemaphoreInfo, which allows attackers to cause a denial of service via a crafted file.

## References
- http://www.securityfocus.com/bid/98943
- https://github.com/ImageMagick/ImageMagick/commit/01843366d6a7b96e22ad7bb67f3df7d9fd4d5d74
- https://github.com/ImageMagick/ImageMagick/issues/491
