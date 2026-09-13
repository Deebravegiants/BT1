# [C] CVE-2017-8283

## Summary
Severity: Critical
Advisory: CVE-2017-8283
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-04-26
Source: https://osv.dev/vulnerability/CVE-2017-8283
Type: osv

## Details
dpkg-source in dpkg 1.3.0 through 1.18.23 is able to use a non-GNU patch program and does not offer a protection mechanism for blank-indented diff hunks, which allows remote attackers to conduct directory traversal attacks via a crafted Debian source package, as demonstrated by use of dpkg-source on NetBSD.

## References
- http://www.securityfocus.com/bid/98064
- http://www.openwall.com/lists/oss-security/2017/04/20/2
