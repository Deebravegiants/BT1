# [H] Apache ActiveMQ AMQP, Apache ActiveMQ, Apache ActiveMQ All: AMQP NIO negative frame size validation bypass leading to DoS

## Summary
Severity: High
Advisory: BIT-activemq-2026-59878
Aliases: CVE-2026-59878
Ecosystem: Bitnami
Published: 2026-08-17
Source: https://osv.dev/vulnerability/BIT-activemq-2026-59878
Type: osv

## Affected
- Bitnami: `activemq` — affected >=6.0.0 <6.2.8

## Details
Improper Input Validation vulnerability in Apache ActiveMQ AMQP, Apache ActiveMQ, Apache ActiveMQ All.

A remote unauthenticated peer that can reach an exposed AMQP NIO connector can trigger denial-of-service behavior by sending a frame size value. This cause the NIO threads to die and if done rapidly enough can lead to exhaustion of the NIO thread pool denying service to other connections.
This issue affects Apache ActiveMQ AMQP: before 5.19.9, from 6.0.0 before 6.2.8; Apache ActiveMQ: before 5.19.9, from 6.0.0 before 6.2.8; Apache ActiveMQ All: before 5.19.9, from 6.0.0 before 6.2.8.

Users are recommended to upgrade to version 5.19.9, 6.2.8, or 6.3.0 which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/07/27/7
- https://lists.apache.org/thread/dnyx4d2oldshcj4lthso7b53y4bqmjvn
- https://nvd.nist.gov/vuln/detail/CVE-2026-59878
