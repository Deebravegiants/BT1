# [M] CVE-2017-9440

## Summary
Severity: Medium
Advisory: CVE-2017-9440
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-06-05
Source: https://osv.dev/vulnerability/CVE-2017-9440
Type: osv

## Details
In ImageMagick 7.0.5-5, a memory leak was found in the function ReadPSDChannel in coders/psd.c, which allows attackers to cause a denial of service via a crafted file.

## References
- http://www.securityfocus.com/bid/98908
- https://github.com/ImageMagick/ImageMagick/issues/462
