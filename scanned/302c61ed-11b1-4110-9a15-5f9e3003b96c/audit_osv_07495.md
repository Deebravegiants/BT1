# [C] BIT-sqlite-2020-35527

## Summary
Severity: Critical
Advisory: BIT-sqlite-2020-35527
Aliases: CVE-2020-35527
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-sqlite-2020-35527
Type: osv

## Affected
- Bitnami: `sqlite` — affected >=3.31.1 <3.31.2

## Details
In SQLite 3.31.1, there is an out of bounds access problem through ALTER TABLE for views that have a nested FROM clause.

## References
- https://security.netapp.com/advisory/ntap-20221111-0007/
- https://www.sqlite.org/src/info/c431b3fd8fd0f6a6
- https://nvd.nist.gov/vuln/detail/CVE-2020-35527
