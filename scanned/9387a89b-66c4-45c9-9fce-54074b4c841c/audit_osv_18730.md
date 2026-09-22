# [M] CVE-2020-35652

## Summary
Severity: Medium
Advisory: CVE-2020-35652
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-01-29
Source: https://osv.dev/vulnerability/CVE-2020-35652
Type: osv

## Details
An issue was discovered in res_pjsip_diversion.c in Sangoma Asterisk before 13.38.0, 14.x through 16.x before 16.15.0, 17.x before 17.9.0, and 18.x before 18.1.0. A crash can occur when a SIP message is received with a History-Info header that contains a tel-uri, or when a SIP 181 response is received that contains a tel-uri in the Diversion header.

## References
- https://downloads.asterisk.org/pub/security/AST-2020-003.html
- https://downloads.asterisk.org/pub/security/AST-2020-004.html
- https://issues.asterisk.org/jira/browse/ASTERISK-29219
- https://issues.asterisk.org/jira/browse/ASTERISK-29191
