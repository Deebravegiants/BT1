# [M] CVE-2017-5498

## Summary
Severity: Medium
Advisory: CVE-2017-5498
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-03-01
Source: https://osv.dev/vulnerability/CVE-2017-5498
Type: osv

## Details
libjasper/include/jasper/jas_math.h in JasPer 1.900.17 allows remote attackers to cause a denial of service (crash) via vectors involving left shift of a negative value.

## References
- http://www.securityfocus.com/bid/95666
- https://blogs.gentoo.org/ago/2017/01/16/jasper-multiple-crashes-with-ubsan/
