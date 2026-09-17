# [M] CVE-2016-0734

## Summary
Severity: Medium
Advisory: CVE-2016-0734
Aliases: GHSA-w525-w93j-rxgm
CVSS: 6.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2016-04-07
Source: https://osv.dev/vulnerability/CVE-2016-0734
Type: osv

## Details
The web-based administration console in Apache ActiveMQ 5.x before 5.13.2 does not send an X-Frame-Options HTTP header, which makes it easier for remote attackers to conduct clickjacking attacks via a crafted web page that contains a (1) FRAME or (2) IFRAME element.

## References
- http://www.openwall.com/lists/oss-security/2016/03/10/11
- http://www.securityfocus.com/bid/84321
- http://www.securitytracker.com/id/1035327
- https://lists.apache.org/thread.html/a859563f05fbe7c31916b3178c2697165bd9bbf5a65d1cf62aef27d2%40%3Ccommits.activemq.apache.org%3E
- http://activemq.apache.org/security-advisories.data/CVE-2016-0734-announcement.txt
- https://access.redhat.com/errata/RHSA-2016:1424
