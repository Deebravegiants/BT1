# [H] Apache ActiveMQ Broker, Apache ActiveMQ, Apache ActiveMQ All: Pre-authentication OpenWire DoS following fix for CVE-2026-49270

## Summary
Severity: High
Advisory: BIT-activemq-2026-50750
Aliases: CVE-2026-50750
Ecosystem: Bitnami
Published: 2026-07-06
Source: https://osv.dev/vulnerability/BIT-activemq-2026-50750
Type: osv

## Affected
- Bitnami: `activemq` — affected >=6.2.6 <6.2.7

## Details
Denial of Service via Out of Memory vulnerability in Apache ActiveMQ Broker, Apache ActiveMQ, Apache ActiveMQ All.

Following the fix for  CVE-2026-49270 an unauthenticated attacker can now cause broker OOM by sending an repeated BrokerInfo commands without sending a ConnectionInfo, until the broker will crash with OOM.
This issue affects Apache ActiveMQ Broker: from 5.19.7 before 5.19.8, from 6.2.6 before 6.2.7; Apache ActiveMQ: from 5.19.7 before 5.19.8, from 6.2.6 before 6.2.7; Apache ActiveMQ All: from 5.19.7 before 5.19.8, from 6.2.6 before 6.2.7.

Users are recommended to upgrade to version 6.2.7, which fixes the issue.

## References
- https://lists.apache.org/thread/nhkmbdym61yp6wwy0dny8w1p46sm87kr
- https://nvd.nist.gov/vuln/detail/CVE-2026-50750
