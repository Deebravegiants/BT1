# [H] CVE-2017-14098

## Summary
Severity: High
Advisory: CVE-2017-14098
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-09-02
Source: https://osv.dev/vulnerability/CVE-2017-14098
Type: osv

## Details
In the pjsip channel driver (res_pjsip) in Asterisk 13.x before 13.17.1 and 14.x before 14.6.1, a carefully crafted tel URI in a From, To, or Contact header could cause Asterisk to crash.

## References
- http://www.securityfocus.com/bid/100583
- http://www.securitytracker.com/id/1039253
- https://issues.asterisk.org/jira/browse/ASTERISK-27152
- http://downloads.asterisk.org/pub/security/AST-2017-007.html
- https://bugs.debian.org/873909
