# [H] CVE-2016-2224

## Summary
Severity: High
Advisory: CVE-2016-2224
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-03-24
Source: https://osv.dev/vulnerability/CVE-2016-2224
Type: osv

## Details
The __decode_dotted function in libc/inet/resolv.c in uClibc-ng before 1.0.12 allows remote DNS servers to cause a denial of service (infinite loop) via vectors involving compressed items in a reply.

## References
- http://www.securityfocus.com/bid/82903
- http://repo.or.cz/uclibc-ng.git/commit/d9c3a16dcab57d6b56225b9a67e9119cc9e2e4ac
- http://www.openwall.com/lists/oss-security/2016/02/05/2
- http://www.openwall.com/lists/oss-security/2016/02/05/3
- https://security-tracker.debian.org/tracker/CVE-2016-2224
