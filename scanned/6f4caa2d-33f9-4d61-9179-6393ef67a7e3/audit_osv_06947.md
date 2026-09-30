# [H] Server crashes in case of the use of exchange

## Summary
Severity: High
Advisory: BIT-mongodb-2026-9746
Aliases: CVE-2026-9746
Ecosystem: Bitnami
Published: 2026-06-22
Source: https://osv.dev/vulnerability/BIT-mongodb-2026-9746
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=8.3.0 <8.3.3

## Details
When using $changestreams and $_requestReshardingResumeToken with the exchange option the server hits an invariant which causes the server to crash. There are no special privileges needed. The user must be logged in to issue the statement.

## References
- https://jira.mongodb.org/browse/SERVER-124190
- https://nvd.nist.gov/vuln/detail/CVE-2026-9746
