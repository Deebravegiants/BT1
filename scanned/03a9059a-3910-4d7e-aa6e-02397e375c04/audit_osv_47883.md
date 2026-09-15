# [M] CVE-2017-14324

## Summary
Severity: Medium
Advisory: CVE-2017-14324
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-09-12
Source: https://osv.dev/vulnerability/CVE-2017-14324
Type: osv

## Details
In ImageMagick 7.0.7-1 Q16, a memory leak vulnerability was found in the function ReadMPCImage in coders/mpc.c, which allows attackers to cause a denial of service via a crafted file.

## References
- http://www.securityfocus.com/bid/100863
- https://github.com/ImageMagick/ImageMagick/issues/739
