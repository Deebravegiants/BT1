# [M] In Spring for Apache Kafka, missing header validation in DeadLetterPublishingRecovererFactory enables denial of service via a poison-pill loop

## Summary
Severity: Medium
Advisory: CVE-2026-59317
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-59317
Type: osv

## Details
DeadLetterPublishingRecovererFactory reads the retry_topic-original-timestamp header from an inbound ConsumerRecord and passes its raw bytes directly to new BigInteger(header.value()) with no length or format validation.
Spring for Apache Kafka 4.1.0
Spring for Apache Kafka 4.0.0 - 4.0.6
Spring for Apache Kafka 3.0.0 - 3.3.16
Spring for Apache Kafka 2.9.0 - 2.9.14
Spring for Apache Kafka 2.8.12 and earlier

## References
- https://spring.io/security/cve-2026-59317
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59317.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-59317
