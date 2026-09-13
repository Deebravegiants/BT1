# [M] CVE-2018-7286

## Summary
Severity: Medium
Advisory: CVE-2018-7286
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-02-22
Source: https://osv.dev/vulnerability/CVE-2018-7286
Type: osv

## Details
An issue was discovered in Asterisk through 13.19.1, 14.x through 14.7.5, and 15.x through 15.2.1, and Certified Asterisk through 13.18-cert2. res_pjsip allows remote authenticated users to crash Asterisk (segmentation fault) by sending a number of SIP INVITE messages on a TCP or TLS connection and then suddenly closing the connection.

## References
- http://downloads.asterisk.org/pub/security/AST-2018-005.html
- http://www.securityfocus.com/bid/103129
- http://www.securitytracker.com/id/1040417
- https://issues.asterisk.org/jira/browse/ASTERISK-27618
- https://www.debian.org/security/2018/dsa-4320
- https://www.exploit-db.com/exploits/44181/
