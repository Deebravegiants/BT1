# [H] Server crash via aggregation pipeline expression with compound wildcard index specification

## Summary
Severity: High
Advisory: BIT-mongodb-2026-13055
Aliases: CVE-2026-13055
Ecosystem: Bitnami
Published: 2026-08-17
Source: https://osv.dev/vulnerability/BIT-mongodb-2026-13055
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=8.3.0 <8.3.7

## Details
The `$_internalIndexKey` aggregation expression can be used by any authenticated user to crash a MongoDB server (mongod). The expression fails to handle compound wildcard index specifications, triggering an internal consistency check that aborts the server process. The user must be able to run an aggregation pipeline.

## References
- https://jira.mongodb.org/browse/SERVER-123081
- https://nvd.nist.gov/vuln/detail/CVE-2026-13055
