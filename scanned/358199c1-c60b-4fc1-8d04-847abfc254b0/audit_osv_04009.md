# [H] Apache ActiveMQ, Apache ActiveMQ All, Apache ActiveMQ Client, Apache ActiveMQ Broker: Unbounded memory allocation in OpenWire property unmarshalling

## Summary
Severity: High
Advisory: BIT-activemq-2026-53917
Aliases: CVE-2026-53917
Ecosystem: Bitnami
Published: 2026-07-06
Source: https://osv.dev/vulnerability/BIT-activemq-2026-53917
Type: osv

## Affected
- Bitnami: `activemq` — affected >=6.0.0 <6.2.7

## Details
Memory Allocation with Excessive Size Value vulnerability in Apache ActiveMQ, Apache ActiveMQ All, Apache ActiveMQ Client, Apache ActiveMQ Broker.

An authenticated user can cause a broker DoS by sending a crafted OpenWire Message with a large encoded size value for the map. OpenWire message property maps are unmarshaled without size validation which can trigger OOM and crash the broker.
This issue affects Apache ActiveMQ: before 5.19.8, from 6.0.0 before 6.2.7; Apache ActiveMQ All: before 5.19.8, from 6.0.0 before 6.2.7; Apache ActiveMQ Client: before 5.19.8, from 6.0.0 before 6.2.7; Apache ActiveMQ Broker: before 5.19.8, from 6.0.0 before 6.2.7.

Users are recommended to upgrade to version 6.2.7 or 5.19.8, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/06/29/14
- https://lists.apache.org/thread/grrd1mwgkgblqjbwkkq6dvmdxd9ov2dx
- https://nvd.nist.gov/vuln/detail/CVE-2026-53917
