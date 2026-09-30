# [H] Server-Side JavaScript Aggregation Expression Memory Safety Issue Leading to Process Termination

## Summary
Severity: High
Advisory: BIT-mongodb-2026-13071
Aliases: CVE-2026-13071
Ecosystem: Bitnami
Published: 2026-08-19
Source: https://osv.dev/vulnerability/BIT-mongodb-2026-13071
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=8.3.0 <8.3.7

## Details
An authenticated user with read access can cause the mongod process to be terminated through certain aggregation expressions that execute server-side JavaScript. The issue involves improper memory handling during document processing.

## References
- https://jira.mongodb.org/browse/SERVER-128473
- https://nvd.nist.gov/vuln/detail/CVE-2026-13071
