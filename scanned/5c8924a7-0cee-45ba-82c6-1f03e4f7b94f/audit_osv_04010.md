# [H] Apache ActiveMQ Broker, Apache ActiveMQ All, Apache ActiveMQ: Temporary destination ownership takeover

## Summary
Severity: High
Advisory: BIT-activemq-2026-54475
Aliases: CVE-2026-54475
Ecosystem: Bitnami
Published: 2026-07-06
Source: https://osv.dev/vulnerability/BIT-activemq-2026-54475
Type: osv

## Affected
- Bitnami: `activemq` — affected >=6.0.0 <6.2.7

## Details
Missing Authorization vulnerability in Apache ActiveMQ Broker, Apache ActiveMQ All, Apache ActiveMQ.

Apache ActiveMQ Classic temporary destinations are expected to be isolated to the connection that created them. The isolation can be broken as this is only checked in the client, allowing a different connection to consume from another connection's temporary
destination.
This issue affects Apache ActiveMQ Broker: before 5.19.8, from 6.0.0 before 6.2.7; Apache ActiveMQ All: before 5.19.8, from 6.0.0 before 6.2.7; Apache ActiveMQ: before 5.19.8, from 6.0.0 before 6.2.7.

Users are recommended to upgrade to version 6.2.7, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/06/29/15
- https://lists.apache.org/thread/85f3q7mkh71y7qwyn6wvgw0bw4jl06ys
- https://nvd.nist.gov/vuln/detail/CVE-2026-54475
