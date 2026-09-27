# [H] Running certain aggregation operations with the SBE engine may lead to unexpected behavior on MongoDB Server

## Summary
Severity: High
Advisory: BIT-mongodb-2025-6706
Aliases: CVE-2025-6706
Ecosystem: Bitnami
Published: 2025-09-16
Source: https://osv.dev/vulnerability/BIT-mongodb-2025-6706
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=8.0.0 <8.0.4

## Details
An authenticated user may trigger a use after free that may result in MongoDB Server crash and other unexpected behavior, even if the user does not have authorization to shut down a server.
The crash is triggered on affected versions by issuing an aggregation framework operation using a specific combination of rarely-used aggregation pipeline expressions. This issue affects MongoDB Server v6.0 version prior to 6.0.21, MongoDB Server v7.0 version prior to 7.0.17 and MongoDB Server v8.0 version prior to 8.0.4 when the SBE engine is enabled.

## References
- https://jira.mongodb.org/browse/SERVER-106746
- https://nvd.nist.gov/vuln/detail/CVE-2025-6706
