# [M] CVE-2016-8685

## Summary
Severity: Medium
Advisory: CVE-2016-8685
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-01-31
Source: https://osv.dev/vulnerability/CVE-2016-8685
Type: osv

## Details
The findnext function in decompose.c in potrace 1.13 allows remote attackers to cause a denial of service (invalid memory access and crash) via a crafted BMP image.

## References
- http://www.openwall.com/lists/oss-security/2016/10/08/17
- http://www.openwall.com/lists/oss-security/2016/10/16/9
- http://www.securityfocus.com/bid/93470
- https://blogs.gentoo.org/ago/2016/08/29/potrace-invalid-memory-access-in-findnext-decompose-c/
