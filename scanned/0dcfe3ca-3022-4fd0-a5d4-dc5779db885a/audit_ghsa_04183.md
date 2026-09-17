# [M] Spring AMQP Core: Missing Certificate and Hostname Verification for amqps URIs in RabbitConnectionFactoryBean

## Summary
Severity: Medium
Advisory: GHSA-p8qj-fj6r-w7q9
CVE: CVE-2026-41714
CWE: CWE-295
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2026-06-10
Source: https://github.com/advisories/GHSA-p8qj-fj6r-w7q9
Type: github-advisory

## Affected
- Maven: `org.springframework.amqp:spring-amqp` — affected >=4.0.0 <4.0.4
- Maven: `org.springframework.amqp:spring-amqp` — affected >=3.2.0 <3.2.11
- Maven: `org.springframework.amqp:spring-amqp` — affected >=3.1.0
- Maven: `org.springframework.amqp:spring-amqp` — affected >=0

## Details
Applications that configure their broker connection via RabbitConnectionFactoryBean.setUri("amqps://...") without also calling setUseSSL(true) get TLS encryption with no certificate validation and no hostname verification.

Affected versions:
Spring AMQP 4.0.0 through 4.0.3; 3.2.0 through 3.2.10; 3.1.0 through 3.1.15; 2.4.0 through 2.4.17.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-41714
- https://github.com/spring-projects/spring-amqp
- https://github.com/spring-projects/spring-amqp/releases/tag/v3.2.11
- https://github.com/spring-projects/spring-amqp/releases/tag/v4.0.4
- https://spring.io/security/cve-2026-41714
