# [H] CVE-2018-19278

## Summary
Severity: High
Advisory: CVE-2018-19278
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-11-14
Source: https://osv.dev/vulnerability/CVE-2018-19278
Type: osv

## Details
Buffer overflow in DNS SRV and NAPTR lookups in Digium Asterisk 15.x before 15.6.2 and 16.x before 16.0.1 allows remote attackers to crash Asterisk via a specially crafted DNS SRV or NAPTR response, because a buffer size is supposed to match an expanded length but actually matches a compressed length.

## References
- https://downloads.asterisk.org/pub/security/AST-2018-010.html
- https://issues.asterisk.org/jira/browse/ASTERISK-28127
