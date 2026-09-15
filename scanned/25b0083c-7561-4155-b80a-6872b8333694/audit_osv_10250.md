# [H] CVE-2017-14607

## Summary
Severity: High
Advisory: CVE-2017-14607
CVSS: 8.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2017-09-20
Source: https://osv.dev/vulnerability/CVE-2017-14607
Type: osv

## Details
In ImageMagick 7.0.7-4 Q16, an out of bounds read flaw related to ReadTIFFImage has been reported in coders/tiff.c. An attacker could possibly exploit this flaw to disclose potentially sensitive memory or cause an application crash.

## References
- http://www.securityfocus.com/bid/100944
- https://usn.ubuntu.com/3681-1/
- https://www.debian.org/security/2017/dsa-4032
- https://www.debian.org/security/2017/dsa-4040
- https://github.com/ImageMagick/ImageMagick/issues/765
