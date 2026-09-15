# [M] CVE-2021-26713

## Summary
Severity: Medium
Advisory: CVE-2021-26713
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-02-19
Source: https://osv.dev/vulnerability/CVE-2021-26713
Type: osv

## Details
A stack-based buffer overflow in res_rtp_asterisk.c in Sangoma Asterisk before 16.16.1, 17.x before 17.9.2, and 18.x before 18.2.1 and Certified Asterisk before 16.8-cert6 allows an authenticated WebRTC client to cause an Asterisk crash by sending multiple hold/unhold requests in quick succession. This is caused by a signedness comparison mismatch.

## References
- https://downloads.asterisk.org/pub/security/
- https://downloads.asterisk.org/pub/security/AST-2021-004.html
- https://issues.asterisk.org/jira/browse/ASTERISK-29205
