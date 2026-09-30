# [M] CVE-2017-17680

## Summary
Severity: Medium
Advisory: CVE-2017-17680
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-12-14
Source: https://osv.dev/vulnerability/CVE-2017-17680
Type: osv

## Details
In ImageMagick 7.0.7-12 Q16, a memory leak vulnerability was found in the function ReadXPMImage in coders/xpm.c, which allows attackers to cause a denial of service via a crafted xpm image file.

## References
- http://www.securityfocus.com/bid/102203
- https://usn.ubuntu.com/3681-1/
- https://github.com/ImageMagick/ImageMagick/issues/873
