# [M] Specially crafted query may result in a denial of service of mongod

## Summary
Severity: Medium
Advisory: BIT-mongodb-2021-20326
Aliases: CVE-2021-20326
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mongodb-2021-20326
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=4.4.0 <4.4.4

## Details
A user authorized to performing a specific type of find query may trigger a denial of service. This issue affects MongoDB Server v4.4 versions prior to 4.4.4.

## References
- https://jira.mongodb.org/browse/SERVER-53929
- https://nvd.nist.gov/vuln/detail/CVE-2021-20326
