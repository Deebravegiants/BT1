# [H] Aggregation Framework Memory Exhaustion Leading to Process Termination

## Summary
Severity: High
Advisory: BIT-mongodb-2026-13076
Aliases: CVE-2026-13076
Ecosystem: Bitnami
Published: 2026-08-19
Source: https://osv.dev/vulnerability/BIT-mongodb-2026-13076
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=8.3.0 <8.3.7

## Details
An authenticated user can cause a {{mongod}} process to be terminated by the operating system under memory pressure by performing a specific data type conversion operation within MongoDB's aggregation framework. The behavior stems from disproportionate memory consumption during this operation, and requires both write access to the database and the ability to run aggregation queries.

## References
- https://jira.mongodb.org/browse/SERVER-128584
- https://nvd.nist.gov/vuln/detail/CVE-2026-13076
