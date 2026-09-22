# [H] In Spring for Apache Kafka, overly broad trusted-package matching in header mappers exposes JDK classes to deserialization

## Summary
Severity: High
Advisory: GHSA-xq69-5h5v-x9x4
CVE: CVE-2026-41731
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-10
Source: https://github.com/advisories/GHSA-xq69-5h5v-x9x4
Type: github-advisory

## Affected
- Maven: `org.springframework.kafka:spring-kafka` — affected >=4.0.0 <4.0.6
- Maven: `org.springframework.kafka:spring-kafka` — affected >=3.3.0 <3.3.16
- Maven: `org.springframework.kafka:spring-kafka` — affected >=3.2.0
- Maven: `org.springframework.kafka:spring-kafka` — affected >=2.9.0
- Maven: `org.springframework.kafka:spring-kafka` — affected >=0

## Details
JsonKafkaHeaderMapper and the deprecated DefaultKafkaHeaderMapper matched type headers against trusted packages using a prefix check, meaning that trusting any package implicitly trusted all of its subpackages. Combined with Jackson's default bean deserialization, a producer could supply crafted header values that caused the consumer to deserialize arbitrary JDK types.

Affected versions:
Spring for Apache Kafka 4.0.0 through 4.0.5; 3.3.0 through 3.3.15; 3.2.0 through 3.2.13; 2.9.0 through 2.9.13; 2.8.0 through 2.8.11.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-41731
- https://github.com/spring-projects/spring-kafka
- https://spring.io/security/cve-2026-41731
