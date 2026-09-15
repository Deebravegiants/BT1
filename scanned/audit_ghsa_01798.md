# [H] Unsafe Deserialization that can Result in Code Execution

## Summary
Severity: High
Advisory: GHSA-v525-c3g5-cg9p
CVE: CVE-2020-36282
CWE: CWE-502
Ecosystem: Maven
Published: 2021-12-10
Source: https://github.com/advisories/GHSA-v525-c3g5-cg9p
Type: github-advisory

## Affected
- Maven: `com.rabbitmq.jms:rabbitmq-jms` — affected >=2.0 <2.2.0
- Maven: `com.rabbitmq.jms:rabbitmq-jms` — affected >=1.0 <1.15.2

## Details
JMS Client for RabbitMQ 1.x before 1.15.2 and 2.x before 2.2.0 is vulnerable to unsafe deserialization that can result in code execution via crafted StreamMessage data.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36282
- https://github.com/rabbitmq/rabbitmq-jms-client/issues/135
- https://github.com/rabbitmq/rabbitmq-jms-client/pull/136/commits/f647e5dbfe055a2ca8cbb16dd70f9d50d888b638
- https://github.com/rabbitmq/rabbitmq-jms-client/releases/tag/v1.15.2
- https://github.com/rabbitmq/rabbitmq-jms-client/releases/tag/v2.2.0
- https://medium.com/@ramon93i7/a99645d0448b
