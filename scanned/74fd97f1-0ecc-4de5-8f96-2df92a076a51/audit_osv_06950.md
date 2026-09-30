# [H] Metadata name collision on $-prefixed fields causes post-auth server crash

## Summary
Severity: High
Advisory: BIT-mongodb-2026-9750
Aliases: CVE-2026-9750
Ecosystem: Bitnami
Published: 2026-06-16
Source: https://osv.dev/vulnerability/BIT-mongodb-2026-9750
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=8.3.0 <8.3.3

## Details
An authenticated user can cause a MongoDB server to crash or return incorrect results by creating documents that interfere with internal metadata processing during query execution. This stems from insufficient separation between user-controlled document fields and internal metadata in certain execution paths.

## References
- https://jira.mongodb.org/browse/SERVER-123633
- https://nvd.nist.gov/vuln/detail/CVE-2026-9750
