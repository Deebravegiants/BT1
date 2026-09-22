# [M] Use-after-free in the MongoDB server query planner may lead to crash or undefined behavior

## Summary
Severity: Medium
Advisory: BIT-mongodb-2025-11979
Aliases: CVE-2025-11979
Ecosystem: Bitnami
Published: 2025-12-06
Source: https://osv.dev/vulnerability/BIT-mongodb-2025-11979
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=8.0.0 <8.0.15

## Details
An authorized user may crash the MongoDB server by causing buffer over-read. This can be done by issuing a DDL operation while queries are being issued, under some conditions. This issue affects MongoDB Server v7.0 versions prior to 7.0.25, MongoDB Server v8.0 versions prior to 8.0.15, and MongoDB Server version 8.2.0.

## References
- https://jira.mongodb.org/browse/SERVER-105873
- https://nvd.nist.gov/vuln/detail/CVE-2025-11979
