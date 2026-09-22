# [M] MongoDB Server (mongod) may crash when generating ftdc

## Summary
Severity: Medium
Advisory: BIT-mongodb-2024-3374
Aliases: CVE-2024-3374
Ecosystem: Bitnami
Published: 2025-10-01
Source: https://osv.dev/vulnerability/BIT-mongodb-2024-3374
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=6.0.0 <6.0.15

## Details
An unauthenticated user can trigger a fatal assertion in the server while generating ftdc diagnostic metrics due to attempting to build a BSON object that exceeds certain memory sizes. This issue affects MongoDB Server v5.0 versions prior to and including 5.0.16 and MongoDB Server v6.0 versions prior to and including 6.0.5.

## References
- https://jira.mongodb.org/browse/SERVER-75601
- https://nvd.nist.gov/vuln/detail/CVE-2024-3374
