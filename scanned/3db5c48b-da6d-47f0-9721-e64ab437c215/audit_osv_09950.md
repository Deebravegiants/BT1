# [H] CVE-2017-12428

## Summary
Severity: High
Advisory: CVE-2017-12428
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-08-04
Source: https://osv.dev/vulnerability/CVE-2017-12428
Type: osv

## Details
In ImageMagick 7.0.6-1, a memory leak vulnerability was found in the function ReadWMFImage in coders/wmf.c, which allows attackers to cause a denial of service in CloneDrawInfo in draw.c.

## References
- http://www.securityfocus.com/bid/100145
- https://www.debian.org/security/2017/dsa-4019
- https://github.com/ImageMagick/ImageMagick/issues/544
