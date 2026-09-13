# [H] CVE-2017-17090

## Summary
Severity: High
Advisory: CVE-2017-17090
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-12-02
Source: https://osv.dev/vulnerability/CVE-2017-17090
Type: osv

## Details
An issue was discovered in chan_skinny.c in Asterisk Open Source 13.18.2 and older, 14.7.2 and older, and 15.1.2 and older, and Certified Asterisk 13.13-cert7 and older. If the chan_skinny (aka SCCP protocol) channel driver is flooded with certain requests, it can cause the asterisk process to use excessive amounts of virtual memory, eventually causing asterisk to stop processing requests of any kind.

## References
- http://www.securitytracker.com/id/1039948
- https://lists.debian.org/debian-lts-announce/2017/12/msg00028.html
- https://www.exploit-db.com/exploits/43992/
- http://downloads.digium.com/pub/security/AST-2017-013.html
- http://www.securityfocus.com/bid/102023
- https://www.debian.org/security/2017/dsa-4076
- https://issues.asterisk.org/jira/browse/ASTERISK-27452
