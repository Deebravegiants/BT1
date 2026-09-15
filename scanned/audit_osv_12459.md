# [M] CVE-2018-12228

## Summary
Severity: Medium
Advisory: CVE-2018-12228
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-06-12
Source: https://osv.dev/vulnerability/CVE-2018-12228
Type: osv

## Details
An issue was discovered in Asterisk Open Source 15.x before 15.4.1. When connected to Asterisk via TCP/TLS, if the client abruptly disconnects, or sends a specially crafted message, then Asterisk gets caught in an infinite loop while trying to read the data stream. This renders the system unusable.

## References
- http://downloads.asterisk.org/pub/security/AST-2018-007.html
- http://www.securityfocus.com/bid/104457
- https://issues.asterisk.org/jira/browse/ASTERISK-27807
