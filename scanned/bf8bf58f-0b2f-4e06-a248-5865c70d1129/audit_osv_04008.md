# [H] Apache ActiveMQ, Apache ActiveMQ All, Apache ActiveMQ Stomp: Unbounded header buffer in STOMP NIO codec

## Summary
Severity: High
Advisory: BIT-activemq-2026-53916
Aliases: CVE-2026-53916
Ecosystem: Bitnami
Published: 2026-07-06
Source: https://osv.dev/vulnerability/BIT-activemq-2026-53916
Type: osv

## Affected
- Bitnami: `activemq` — affected >=6.0.0 <6.2.7

## Details
Memory Allocation with Excessive Size Value vulnerability in Apache ActiveMQ, Apache ActiveMQ All, Apache ActiveMQ Stomp.


An unauthenticated client that opens a STOMP NIO connection can send header bytes that never terminate which makes the broker buffer them without limit, exhausting the JVM heap. 
This issue affects Apache ActiveMQ: before 5.19.8, from 6.0.0 before 6.2.7; Apache ActiveMQ All: before 5.19.8, from 6.0.0 before 6.2.7; Apache ActiveMQ Stomp: before 5.19.8, from 6.0.0 before 6.2.7.

Users are recommended to upgrade to version 6.2.7 or 5.19.8, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/06/29/13
- https://lists.apache.org/thread/07hjsj88hqgsb7vvg6ttsj56ts9vjs5n
- https://nvd.nist.gov/vuln/detail/CVE-2026-53916
