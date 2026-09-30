# [H] Stack memory disclosure in filemd5 command

## Summary
Severity: High
Advisory: BIT-mongodb-2026-4147
Aliases: CVE-2026-4147
Ecosystem: Bitnami
Published: 2026-05-13
Source: https://osv.dev/vulnerability/BIT-mongodb-2026-4147
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=8.3.0 <8.3.1

## Details
An authenticated user with the read role may read limited amounts of uninitialized stack memory via specially-crafted issuances of the filemd5 command.

## References
- https://jira.mongodb.org/browse/SERVER-119317
- https://nvd.nist.gov/vuln/detail/CVE-2026-4147
