# [M] Apache ActiveMQ Broker, Apache ActiveMQ All, Apache ActiveMQ: Authorization bypass via temporary composite destinations

## Summary
Severity: Medium
Advisory: BIT-activemq-2026-61487
Aliases: CVE-2026-61487
Ecosystem: Bitnami
Published: 2026-08-17
Source: https://osv.dev/vulnerability/BIT-activemq-2026-61487
Type: osv

## Affected
- Bitnami: `activemq` — affected >=6.0.0 <6.2.8

## Details
Improper Authorization vulnerability in Apache ActiveMQ Broker, Apache ActiveMQ All, Apache ActiveMQ.

 An authenticated low-privilege user can bypass a per-destination
write ACL by sending to an ActiveMQ temporary composite destination whose physical name is a
comma-separated composite of real queues. This allows publishing messages to any of the destinations in the list without proper write ACL permissions because the authorization check is bypassed due to the composite destination being marked as temporary.
This issue affects Apache ActiveMQ Broker: before 5.19.9, from 6.0.0 before 6.2.8; Apache ActiveMQ All: before 5.19.9, from 6.0.0 before 6.2.8; Apache ActiveMQ: before 5.19.9, from 6.0.0 before 6.2.8.

Users are recommended to upgrade to version 5.19.9, 6.2.8 or 6.3.0, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/07/27/8
- https://lists.apache.org/thread/6rwn6cq65dy4lhmsmjf2bxnhbmhkcswz
- https://nvd.nist.gov/vuln/detail/CVE-2026-61487
