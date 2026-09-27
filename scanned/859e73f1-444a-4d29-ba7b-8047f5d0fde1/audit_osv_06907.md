# [H] MongoDB mongos Improper Validation of Internal Flags in Queryable Encryption Write Commands on Sharded Clusters

## Summary
Severity: High
Advisory: BIT-mongodb-2026-13062
Aliases: CVE-2026-13062
Ecosystem: Bitnami
Published: 2026-08-17
Source: https://osv.dev/vulnerability/BIT-mongodb-2026-13062
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=8.3.0 <8.3.7

## Details
An authenticated user with write privileges on a Queryable Encryption-enabled collection may be able to modify internal encryption metadata fields that are intended to be server-controlled, by sending crafted write commands through the mongos router on a sharded cluster. This can result in corruption of encrypted query correctness.

## References
- https://jira.mongodb.org/browse/SERVER-127831
- https://nvd.nist.gov/vuln/detail/CVE-2026-13062
