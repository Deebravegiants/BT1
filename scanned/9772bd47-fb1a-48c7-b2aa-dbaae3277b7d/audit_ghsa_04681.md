# [M] Spring for Apache Kafka: Improper Validation of Retry Topic Header Values Leads to Retry Sequence Manipulation

## Summary
Severity: Medium
Advisory: GHSA-53w6-v7cv-fc9h
CVE: CVE-2026-41727
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-10
Source: https://github.com/advisories/GHSA-53w6-v7cv-fc9h
Type: github-advisory

## Affected
- Maven: `org.springframework.kafka:spring-kafka` — affected >=4.0.0 <4.0.6
- Maven: `org.springframework.kafka:spring-kafka` — affected >=3.3.0 <3.3.16
- Maven: `org.springframework.kafka:spring-kafka` — affected >=3.2.0
- Maven: `org.springframework.kafka:spring-kafka` — affected >=2.9.0
- Maven: `org.springframework.kafka:spring-kafka` — affected >=0

## Details
Spring Kafka's retry topic infrastructure did not sufficiently validate user-controlled header values before acting on them. A producer could send a record with a crafted retry_topic-attempts header to supply an out-of-range attempt count and cause the retry topic router to misidentify where the message was in the retry sequence.

Affected versions:
Spring for Apache Kafka 4.0.0 through 4.0.5; 3.3.0 through 3.3.15; 3.2.0 through 3.2.13; 2.9.0 through 2.9.13; 2.8.0 through 2.8.11.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-41727
- https://github.com/spring-projects/spring-kafka
- https://github.com/spring-projects/spring-kafka/releases/tag/v3.3.16
- https://github.com/spring-projects/spring-kafka/releases/tag/v4.0.6
- https://spring.io/security/cve-2026-41727
