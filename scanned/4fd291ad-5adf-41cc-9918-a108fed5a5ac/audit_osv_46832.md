# [H] CVE-2015-5259

## Summary
Severity: High
Advisory: CVE-2015-5259
CVSS: 8.6 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:H)
Published: 2016-01-08
Source: https://osv.dev/vulnerability/CVE-2015-5259
Type: osv

## Details
Integer overflow in the read_string function in libsvn_ra_svn/marshal.c in Apache Subversion 1.9.x before 1.9.3 allows remote attackers to execute arbitrary code via an svn:// protocol string, which triggers a heap-based buffer overflow and an out-of-bounds read.

## References
- http://subversion.apache.org/security/CVE-2015-5259-advisory.txt
- https://security.gentoo.org/glsa/201610-05
- http://www.securityfocus.com/bid/82300
- http://www.securitytracker.com/id/1034469
