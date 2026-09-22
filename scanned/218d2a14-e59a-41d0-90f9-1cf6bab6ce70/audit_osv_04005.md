# [H] Apache ActiveMQ Client, Apache ActiveMQ, Apache ActiveMQ All: Pre-authentication OpenWire memory-allocation DoS during wire format negotiation

## Summary
Severity: High
Advisory: BIT-activemq-2026-50734
Aliases: CVE-2026-50734
Ecosystem: Bitnami
Published: 2026-07-06
Source: https://osv.dev/vulnerability/BIT-activemq-2026-50734
Type: osv

## Affected
- Bitnami: `activemq` — affected >=6.0.0 <6.2.7

## Details
Memory Allocation with Excessive Size Value vulnerability in Apache ActiveMQ Client, Apache ActiveMQ, Apache ActiveMQ All.

An unauthenticated network attacker can cause a broker DoS by sending a crafted WireFormatInfo frame with a malicious large size value. The value is not validate and causes the broker to attempt allocation during pre-auth negotiation which can trigger OOM and crash the broker.
This issue affects Apache ActiveMQ Client: before 5.19.8, from 6.0.0 before 6.2.7; Apache ActiveMQ: before 5.19.8, from 6.0.0 before 6.2.7; Apache ActiveMQ All: before 5.19.8, from 6.0.0 before 6.2.7.

Users are recommended to upgrade to version 6.2.7 or 5.19.8, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/06/29/10
- https://lists.apache.org/thread/nxso951fnvf72qf9m475mpz4yf931xk0
- https://nvd.nist.gov/vuln/detail/CVE-2026-50734
