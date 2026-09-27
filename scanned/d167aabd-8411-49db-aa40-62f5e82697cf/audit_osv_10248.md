# [H] CVE-2017-14603

## Summary
Severity: High
Advisory: CVE-2017-14603
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-10-10
Source: https://osv.dev/vulnerability/CVE-2017-14603
Type: osv

## Details
In Asterisk 11.x before 11.25.3, 13.x before 13.17.2, and 14.x before 14.6.2 and Certified Asterisk 11.x before 11.6-cert18 and 13.x before 13.13-cert6, insufficient RTCP packet validation could allow reading stale buffer contents and when combined with the "nat" and "symmetric_rtp" options allow redirecting where Asterisk sends the next RTCP report.

## References
- http://downloads.asterisk.org/pub/security/AST-2017-008.html
- http://www.debian.org/security/2017/dsa-3990
- https://issues.asterisk.org/jira/browse/ASTERISK-27274
