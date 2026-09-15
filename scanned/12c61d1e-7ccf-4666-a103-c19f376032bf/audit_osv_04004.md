# [H] Apache ActiveMQ: Authenticated web users retain admin access by default in the Web Console

## Summary
Severity: High
Advisory: BIT-activemq-2026-49877
Aliases: CVE-2026-49877
Ecosystem: Bitnami
Published: 2026-07-06
Source: https://osv.dev/vulnerability/BIT-activemq-2026-49877
Type: osv

## Affected
- Bitnami: `activemq` — affected >=6.0.0 <6.2.7

## Details
Improper Authorization vulnerability in Apache ActiveMQ.

An authenticated low-privilege Web Console user by default can access /admin/* paths in the Web Console. The default Jetty settings incorrectly did not limit those paths to only admins.
This issue affects Apache ActiveMQ: before 5.19.8, from 6.0.0 before 6.2.7.

Users are recommended to upgrade to version 6.2.7 or 5.19.8, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/06/29/9
- https://lists.apache.org/thread/w82vtc3q02j5ot94tnyy1197y3wb98hl
- https://nvd.nist.gov/vuln/detail/CVE-2026-49877
