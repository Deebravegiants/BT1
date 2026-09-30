# [M] In Spring for Apache Kafka, unbounded delegate cache keyed on user-controlled, potentially malicious selector header

## Summary
Severity: Medium
Advisory: GHSA-xvfq-4q6q-gxx7
CVE: CVE-2026-41726
CWE: CWE-770
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-10
Source: https://github.com/advisories/GHSA-xvfq-4q6q-gxx7
Type: github-advisory

## Affected
- Maven: `org.springframework.kafka:spring-kafka` — affected >=4.0.0 <4.0.6
- Maven: `org.springframework.kafka:spring-kafka` — affected >=3.3.0 <3.3.16
- Maven: `org.springframework.kafka:spring-kafka` — affected >=3.2.0
- Maven: `org.springframework.kafka:spring-kafka` — affected >=2.9.0
- Maven: `org.springframework.kafka:spring-kafka` — affected >=0

## Details
When an application opts into DelegatingDeserializer, a producer can grow the consumer's heap without bound by sending records with unique random spring.kafka.serialization.selector header values, eventually causing GC thrash and OutOfMemoryError.

Affected versions:
Spring for Apache Kafka 4.0.0 through 4.0.5; 3.3.0 through 3.3.15; 3.2.0 through 3.2.13; 2.9.0 through 2.9.13; 2.8.0 through 2.8.11.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-41726
- https://github.com/spring-projects/spring-kafka/issues/4489
- https://github.com/spring-projects/spring-kafka/commit/ca2337ba789c5778a10197bda17a62915247ff6c
- https://github.com/spring-projects/spring-kafka
- https://spring.io/security/cve-2026-41726
