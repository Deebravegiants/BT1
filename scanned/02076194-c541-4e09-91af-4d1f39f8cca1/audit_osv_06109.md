# [M] Apache Kafka: Improper Authorization in CONSUMER_GROUP_DESCRIBE API

## Summary
Severity: Medium
Advisory: BIT-kafka-2026-41115
Aliases: CVE-2026-41115
Ecosystem: Bitnami
Published: 2026-06-05
Source: https://osv.dev/vulnerability/BIT-kafka-2026-41115
Type: osv

## Affected
- Bitnami: `kafka` — affected >=4.0.0 <4.3.1

## Details
An improper authorization vulnerability has been identified in Apache Kafka.

The implementation of the CONSUMER_GROUP_DESCRIBE (69) API validates the DESCRIBE operation on the GROUP resource instead of the READ operation that documented in the official kafka documentation and the KIP-848. This discrepancy can result in misconfigured Access Control Lists (ACLs) and unintended security postures, like granting READ permission to users who should not be able to join/sync groups, or allowing users without READ permission (but with DESCRIBE permission) to access sensitive group metadata.

The correct permission for CONSUMER_GROUP_DESCRIBE API is DESCRIBE GROUP so the current implementation is correct. However, the kafka documentation as well as the KIP-848 will be updated to reflect the correct permission. We advise the Kafka users to review existing group ACLs to ensure the principle of least privilege.

## References
- http://www.openwall.com/lists/oss-security/2026/06/02/5
- https://kafka.apache.org/cve-list
- https://nvd.nist.gov/vuln/detail/CVE-2026-41115
