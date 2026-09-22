# [C] CVE-2014-4650

## Summary
Severity: Critical
Advisory: CVE-2014-4650
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-02-20
Source: https://osv.dev/vulnerability/CVE-2014-4650
Type: osv

## Details
The CGIHTTPServer module in Python 2.7.5 and 3.3.4 does not properly handle URLs in which URL encoding is used for path separators, which allows remote attackers to read script source code or conduct directory traversal attacks and execute unintended code via a crafted character sequence, as demonstrated by a %2f separator.

## References
- http://bugs.python.org/issue21766
- http://openwall.com/lists/oss-security/2014/06/26/3
- https://access.redhat.com/security/cve/cve-2014-4650
- http://openwall.com/lists/oss-security/2014/06/26/3
- http://bugs.python.org/issue21766
- http://bugs.python.org/issue21766
