# [H] Improper Validation of Client-Supplied Command Parameters Allowing Role-Based Access Control Bypass

## Summary
Severity: High
Advisory: BIT-mongodb-2026-13059
Aliases: CVE-2026-13059
Ecosystem: Bitnami
Published: 2026-08-17
Source: https://osv.dev/vulnerability/BIT-mongodb-2026-13059
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=8.3.0 <8.3.7

## Details
An authenticated user with low privileges may be able to perform unauthorized reads and writes on data protected by role-based query-level access controls, due to insufficient validation of certain client-supplied command parameters. The issue affects find, update, delete, and aggregate commands in non-apiStrict configurations.

## References
- https://jira.mongodb.org/browse/SERVER-128433
- https://nvd.nist.gov/vuln/detail/CVE-2026-13059
