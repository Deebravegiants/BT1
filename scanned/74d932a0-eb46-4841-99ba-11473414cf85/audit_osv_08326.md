# [H] CVE-2016-2225

## Summary
Severity: High
Advisory: CVE-2016-2225
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-03-24
Source: https://osv.dev/vulnerability/CVE-2016-2225
Type: osv

## Details
The __read_etc_hosts_r function in libc/inet/resolv.c in uClibc-ng before 1.0.12 allows remote DNS servers to cause a denial of service (infinite loop) via a crafted packet.

## References
- http://www.securityfocus.com/bid/82903
- http://repo.or.cz/uclibc-ng.git/commit/6932f2282ba0578d6ca2f21eead920d6b78bc93c
- http://www.openwall.com/lists/oss-security/2016/02/05/2
- http://www.openwall.com/lists/oss-security/2016/02/05/3
- https://security-tracker.debian.org/tracker/CVE-2016-2225
