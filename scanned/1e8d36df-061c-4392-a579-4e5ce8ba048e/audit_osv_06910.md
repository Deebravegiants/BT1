# [H] Server-Side JavaScript DBPointer BSON Serialization Memory Disclosure

## Summary
Severity: High
Advisory: BIT-mongodb-2026-13066
Aliases: CVE-2026-13066
Ecosystem: Bitnami
Published: 2026-08-17
Source: https://osv.dev/vulnerability/BIT-mongodb-2026-13066
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=8.3.0 <8.3.7

## Details
Improper handling of DBPointer objects during BSON serialization in MongoDB's server-side JavaScript engine can result in internal process memory contents being included in data returned to the client. This constitutes an unintended information disclosure affecting deployments that use server-side JavaScript.

## References
- https://jira.mongodb.org/browse/SERVER-127694
- https://nvd.nist.gov/vuln/detail/CVE-2026-13066
