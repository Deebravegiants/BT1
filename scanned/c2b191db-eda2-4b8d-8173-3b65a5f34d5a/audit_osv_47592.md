# [M] CVE-2016-8697

## Summary
Severity: Medium
Advisory: CVE-2016-8697
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-01-31
Source: https://osv.dev/vulnerability/CVE-2016-8697
Type: osv

## Details
The bm_new function in bitmap.h in potrace before 1.13 allows remote attackers to cause a denial of service (divide-by-zero error and crash) via a crafted BMP image.

## References
- http://www.openwall.com/lists/oss-security/2016/10/16/12
- http://www.securityfocus.com/bid/93778
- https://blogs.gentoo.org/ago/2016/08/08/potrace-divide-by-zero-in-bm_new-bitmap-h/
- http://www.openwall.com/lists/oss-security/2016/08/18/11
