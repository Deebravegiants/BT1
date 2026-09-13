# [M] CVE-2020-28242

## Summary
Severity: Medium
Advisory: CVE-2020-28242
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-11-06
Source: https://osv.dev/vulnerability/CVE-2020-28242
Type: osv

## Details
An issue was discovered in Asterisk Open Source 13.x before 13.37.1, 16.x before 16.14.1, 17.x before 17.8.1, and 18.x before 18.0.1 and Certified Asterisk before 16.8-cert5. If Asterisk is challenged on an outbound INVITE and the nonce is changed in each response, Asterisk will continually send INVITEs in a loop. This causes Asterisk to consume more and more memory since the transaction will never terminate (even if the call is hung up), ultimately leading to a restart or shutdown of Asterisk. Outbound authentication must be configured on the endpoint for this to occur.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/QUS54QTQCYKR36EIULYD544GXDA644HB/
- http://downloads.asterisk.org/pub/security/AST-2020-002.html
- https://lists.debian.org/debian-lts-announce/2022/04/msg00001.html
