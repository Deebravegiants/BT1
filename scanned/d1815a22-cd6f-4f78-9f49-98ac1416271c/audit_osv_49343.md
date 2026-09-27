# [M] CVE-2019-10649

## Summary
Severity: Medium
Advisory: CVE-2019-10649
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-03-30
Source: https://osv.dev/vulnerability/CVE-2019-10649
Type: osv

## Details
In ImageMagick 7.0.8-36 Q16, there is a memory leak in the function SVGKeyValuePairs of coders/svg.c, which allows an attacker to cause a denial of service via a crafted image file.

## References
- http://www.securityfocus.com/bid/107645
- https://usn.ubuntu.com/4034-1/
- https://www.debian.org/security/2020/dsa-4712
- https://github.com/ImageMagick/ImageMagick/issues/1533
