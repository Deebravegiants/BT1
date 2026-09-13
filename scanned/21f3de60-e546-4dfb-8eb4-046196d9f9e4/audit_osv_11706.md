# [H] CVE-2017-9358

## Summary
Severity: High
Advisory: CVE-2017-9358
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-06-02
Source: https://osv.dev/vulnerability/CVE-2017-9358
Type: osv

## Details
A memory exhaustion vulnerability exists in Asterisk Open Source 13.x before 13.15.1 and 14.x before 14.4.1 and Certified Asterisk 13.13 before 13.13-cert4, which can be triggered by sending specially crafted SCCP packets causing an infinite loop and leading to memory exhaustion (by message logging in that loop).

## References
- http://www.securitytracker.com/id/1038531
- http://downloads.asterisk.org/pub/security/AST-2017-004.txt
- http://www.securityfocus.com/bid/98573
- https://bugs.debian.org/863906
