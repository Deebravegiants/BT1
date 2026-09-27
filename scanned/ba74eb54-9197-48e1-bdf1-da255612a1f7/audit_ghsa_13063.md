# [H] Spring-Kafka has Java Deserialization vulnerability When Improperly Configured

## Summary
Severity: High
Advisory: GHSA-crqf-q9fp-hwjw
CVE: CVE-2023-34040
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-08-24
Source: https://github.com/advisories/GHSA-crqf-q9fp-hwjw
Type: github-advisory

## Affected
- Maven: `org.springframework.kafka:spring-kafka` — affected >=2.8.1 <2.9.11
- Maven: `org.springframework.kafka:spring-kafka` — affected >=3.0.0 <3.0.10

## Details
In Spring for Apache Kafka 3.0.9 and earlier and versions 2.9.10 and earlier, a possible deserialization attack vector existed, but only if unusual configuration was applied. An attacker would have to construct a malicious serialized object in one of the deserialization exception record headers.

Specifically, an application is vulnerable when all of the following are true:

  *  The user does not configure an ErrorHandlingDeserializer for the key and/or value of the record
  *  The user explicitly sets container properties checkDeserExWhenKeyNull and/or checkDeserExWhenValueNull container properties to true.
  *  The user allows untrusted sources to publish to a Kafka topic


By default, these properties are false, and the container only attempts to deserialize the headers if an ErrorHandlingDeserializer is configured. The ErrorHandlingDeserializer prevents the vulnerability by removing any such malicious headers before processing the record.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-34040
- https://github.com/spring-projects/spring-kafka/commit/25ac793a78725e2ca4a3a2888a1506a4bfcf0c9d
- https://github.com/spring-projects/spring-kafka/commit/eb779679812f61a8553ced3d0e4069dca65560ed
- https://github.com/spring-projects/spring-kafka
- https://spring.io/security/cve-2023-34040
