# [H] ExpressionContext use-after-free in classic engine $lookup and $graphLookup aggregation operators

## Summary
Severity: High
Advisory: BIT-mongodb-2026-4148
Aliases: CVE-2026-4148
Ecosystem: Bitnami
Published: 2026-05-13
Source: https://osv.dev/vulnerability/BIT-mongodb-2026-4148
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=8.3.0 <8.3.1

## Details
A use-after-free vulnerability can be triggered in sharded clusters by an authenticated user with the read role who issues a specially crafted $lookup or $graphLookup aggregation pipeline.

## References
- https://jira.mongodb.org/browse/SERVER-119319
- https://nvd.nist.gov/vuln/detail/CVE-2026-4148
