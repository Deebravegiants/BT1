# [M] Post-authentication CPU utilization DoS via $trim/$ltrim/$rtrim operators

## Summary
Severity: Medium
Advisory: BIT-mongodb-2026-8202
Aliases: CVE-2026-8202
Ecosystem: Bitnami
Published: 2026-05-19
Source: https://osv.dev/vulnerability/BIT-mongodb-2026-8202
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=8.3.0 <8.3.2

## Details
Using a densely populated chars mask and a large input string in the MongoDB aggregation operators $trim, $ltrim, and $rtrim, an authenticated user with aggregation permissions can pin CPU utilization at 100% for an extended period of time.

This issue impacts MongoDB Server v7.0 versions prior to 7.0.34, v8.0 versions prior to 8.0.23, v8.2 versions prior to 8.2.9 and v8.3 versions prior to 8.3.2.

## References
- https://jira.mongodb.org/browse/SERVER-120668
- https://nvd.nist.gov/vuln/detail/CVE-2026-8202
