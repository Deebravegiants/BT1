# [H] A user with read access can cause a DoS by executing a specifically crafted query to consume a large amount of RAM

## Summary
Severity: High
Advisory: BIT-mongodb-2026-13056
Aliases: CVE-2026-13056
Ecosystem: Bitnami
Published: 2026-08-17
Source: https://osv.dev/vulnerability/BIT-mongodb-2026-13056
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=8.3.0 <8.3.7

## Details
Using expressions that generate large arrays it is possible to craft a query that creates very large intermediate objects in memory, causing the server to crash with OOM error.

## References
- https://jira.mongodb.org/browse/SERVER-124355
- https://nvd.nist.gov/vuln/detail/CVE-2026-13056
