# [H] Apache ActiveMQ, Apache ActiveMQ All, Apache ActiveMQ Stomp: STOMP negative content-length enables denial of service

## Summary
Severity: High
Advisory: BIT-activemq-2026-49432
Aliases: CVE-2026-49432
Ecosystem: Bitnami
Published: 2026-07-06
Source: https://osv.dev/vulnerability/BIT-activemq-2026-49432
Type: osv

## Affected
- Bitnami: `activemq` — affected >=6.0.0 <6.2.7

## Details
Improper Input Validation vulnerability in Apache ActiveMQ, Apache ActiveMQ All, Apache ActiveMQ Stomp.

A remote unauthenticated peer that can reach an exposed STOMP connector can trigger denial-of-service behavior by sending a negative content-length. For the NIO STOMP transport, an attacker can keep streaming body bytes and grow the per-connection command buffer beyond configured limits to cause OOM. For the blocking STOMP protocol, an error will instead force abnormal transport exception handling for the affected connection and closure.
This issue affects Apache ActiveMQ: before 5.19.8, from 6.0.0 before 6.2.7; Apache ActiveMQ All: before 5.19.8, from 6.0.0 before 6.2.7; Apache ActiveMQ Stomp: before 5.19.8, from 6.0.0 before 6.2.7.




Users are recommended to upgrade to version 6.2.7 or 5.19.8, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/06/29/7
- https://lists.apache.org/thread/fsjb26605syqr8xks249h8gkp86t55d2
- https://nvd.nist.gov/vuln/detail/CVE-2026-49432
