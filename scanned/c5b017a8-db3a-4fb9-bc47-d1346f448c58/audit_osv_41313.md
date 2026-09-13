# [M] In Spring for Apache Kafka, SSRF via DNS resolution triggered by untrusted java.net types in header mapper default trusted packages

## Summary
Severity: Medium
Advisory: CVE-2026-59278
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-59278
Type: osv

## Details
JsonKafkaHeaderMapper and DefaultKafkaHeaderMapper include java.net in their default trusted packages list. When these mappers are used — which is the default configuration for all @KafkaListener consumers — an external Kafka producer can inject a java.net.InetAddress type via the spring_json_header_types message header.
Spring for Apache Kafka 4.1.0
Spring for Apache Kafka 4.0.0 - 4.0.6
Spring for Apache Kafka 3.0.0 - 3.3.16
Spring for Apache Kafka 2.9.0 - 2.9.14
Spring for Apache Kafka 2.8.12 and earlier

## References
- https://spring.io/security/cve-2026-59278
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59278.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-59278
