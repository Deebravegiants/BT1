# [M] Spring AMQP Has Predictable Correlation IDs in RabbitTemplate.sendAndReceive() with Fixed Reply Queue

## Summary
Severity: Medium
Advisory: GHSA-p5f7-rjhp-pxvc
CVE: CVE-2026-41701
CWE: CWE-330
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-06-10
Source: https://github.com/advisories/GHSA-p5f7-rjhp-pxvc
Type: github-advisory

## Affected
- Maven: `org.springframework.amqp:spring-amqp` — affected >=4.0.0 <4.0.4
- Maven: `org.springframework.amqp:spring-amqp` — affected >=3.2.0 <3.2.11
- Maven: `org.springframework.amqp:spring-amqp` — affected >=3.1.0
- Maven: `org.springframework.amqp:spring-amqp` — affected >=0

## Details
Correlation IDs for replies in the RabbitTemplate.sendAndReceive() with the fixed reply queue are predictable due to internal simple counter.

Affected versions:
Spring AMQP 4.0.0 through 4.0.3; 3.2.0 through 3.2.10; 3.1.0 through 3.1.15; 2.4.0 through 2.4.17.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-41701
- https://github.com/spring-projects/spring-amqp
- https://github.com/spring-projects/spring-amqp/releases/tag/v3.2.11
- https://github.com/spring-projects/spring-amqp/releases/tag/v4.0.4
- https://spring.io/security/cve-2026-41701
