# [H] Memory safety issues in slot-based execution hash table spill

## Summary
Severity: High
Advisory: BIT-mongodb-2026-4358
Aliases: CVE-2026-4358
Ecosystem: Bitnami
Published: 2026-04-06
Source: https://osv.dev/vulnerability/BIT-mongodb-2026-4358
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=8.2.0 <8.2.6

## Details
A specially crafted aggregation query with $lookup by an authenticated user with write privileges can cause a double-free or use-after-free memory issue in the slot-based execution (SBE) engine when an in-memory hash table is spilled to disk.

## References
- https://jira.mongodb.org/browse/SERVER-118849
- https://nvd.nist.gov/vuln/detail/CVE-2026-4358
