# [H] CVE-2016-6264

## Summary
Severity: High
Advisory: CVE-2016-6264
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-01-27
Source: https://osv.dev/vulnerability/CVE-2016-6264
Type: osv

## Details
Integer signedness error in libc/string/arm/memset.S in uClibc and uClibc-ng before 1.0.16 allows context-dependent attackers to cause a denial of service (crash) via a negative length value to the memset function.

## References
- http://mailman.uclibc-ng.org/pipermail/devel/2016-July/001067.html
- http://mailman.uclibc-ng.org/pipermail/devel/2016-May/000890.html
- http://www.securityfocus.com/bid/91492
- http://www.openwall.com/lists/oss-security/2016/06/29/3
- http://www.openwall.com/lists/oss-security/2016/07/21/2
- http://www.openwall.com/lists/oss-security/2016/07/21/6
