# [M] Improper neutralization of null byte leads to read overrun

## Summary
Severity: Medium
Advisory: BIT-mongodb-2020-7928
Aliases: CVE-2020-7928
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mongodb-2020-7928
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=4.5.0 <4.5.1

## Details
A user authorized to perform database queries may trigger a read overrun and access arbitrary memory by issuing specially crafted queries. This issue affects MongoDB Server v4.4 versions prior to 4.4.1; MongoDB Server v4.2 versions prior to 4.2.9; MongoDB Server v4.0 versions prior to 4.0.20 and MongoDB Server v3.6 versions prior to 3.6.20.

## References
- https://jira.mongodb.org/browse/SERVER-49404
- https://nvd.nist.gov/vuln/detail/CVE-2020-7928
