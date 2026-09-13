# [M] CVE-2016-2232

## Summary
Severity: Medium
Advisory: CVE-2016-2232
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-02-22
Source: https://osv.dev/vulnerability/CVE-2016-2232
Type: osv

## Details
Asterisk Open Source 1.8.x, 11.x before 11.21.1, 12.x, and 13.x before 13.7.1 and Certified Asterisk 1.8.28, 11.6 before 11.6-cert12, and 13.1 before 13.1-cert3 allow remote authenticated users to cause a denial of service (uninitialized pointer dereference and crash) via a zero length error correcting redundancy packet for a UDPTL FAX packet that is lost.

## References
- http://www.securitytracker.com/id/1034931
- http://downloads.asterisk.org/pub/security/AST-2016-003.html
- http://www.debian.org/security/2016/dsa-3700
