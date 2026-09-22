# [M] CVE-2017-10800

## Summary
Severity: Medium
Advisory: CVE-2017-10800
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-07-03
Source: https://osv.dev/vulnerability/CVE-2017-10800
Type: osv

## Details
When GraphicsMagick 1.3.25 processes a MATLAB image in coders/mat.c, it can lead to a denial of service (OOM) in ReadMATImage() if the size specified for a MAT Object is larger than the actual amount of data.

## References
- http://www.securityfocus.com/bid/99356
- https://www.debian.org/security/2018/dsa-4321
- http://hg.code.sf.net/p/graphicsmagick/code/rev/e5761e3a2012
