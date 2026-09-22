# [M] profile command may permit unauthorized configuration

## Summary
Severity: Medium
Advisory: BIT-mongodb-2026-25609
Aliases: CVE-2026-25609
Ecosystem: Bitnami
Published: 2026-02-26
Source: https://osv.dev/vulnerability/BIT-mongodb-2026-25609
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=8.2.0 <8.2.4

## Details
Incorrect validation of the profile command may result in the determination that a request altering the 'filter' is read-only.

## References
- https://jira.mongodb.org/browse/SERVER-112952
- https://nvd.nist.gov/vuln/detail/CVE-2026-25609
