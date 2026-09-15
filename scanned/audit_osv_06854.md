# [M] Specially crafted regex query can cause DoS

## Summary
Severity: Medium
Advisory: BIT-mongodb-2020-7929
Aliases: CVE-2020-7929
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mongodb-2020-7929
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=4.0.0 <4.0.20

## Details
A user authorized to perform database queries may trigger denial of service by issuing specially crafted query contain a type of regex. This issue affects MongoDB Server v3.6 versions prior to 3.6.21 and MongoDB Server v4.0 versions prior to 4.0.20.

## References
- https://jira.mongodb.org/browse/SERVER-51083
- https://nvd.nist.gov/vuln/detail/CVE-2020-7929
