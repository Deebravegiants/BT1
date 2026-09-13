# [H] CVE-2017-9049

## Summary
Severity: High
Advisory: CVE-2017-9049
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-05-18
Source: https://osv.dev/vulnerability/CVE-2017-9049
Type: osv

## Details
libxml2 20904-GITv2.9.4-16-g0741801 is vulnerable to a heap-based buffer over-read in the xmlDictComputeFastKey function in dict.c. This vulnerability causes programs that use libxml2, such as PHP, to crash. This vulnerability exists because of an incomplete fix for libxml2 Bug 759398.

## References
- https://lists.apache.org/thread.html/r58af02e294bd07f487e2c64ffc0a29b837db5600e33b6e698b9d696b%40%3Cissues.bookkeeper.apache.org%3E
- https://lists.apache.org/thread.html/rf4c02775860db415b4955778a131c2795223f61cb8c6a450893651e4%40%3Cissues.bookkeeper.apache.org%3E
- http://www.debian.org/security/2017/dsa-3952
- http://www.securityfocus.com/bid/98601
- https://security.gentoo.org/glsa/201711-01
- http://www.openwall.com/lists/oss-security/2017/05/15/1
