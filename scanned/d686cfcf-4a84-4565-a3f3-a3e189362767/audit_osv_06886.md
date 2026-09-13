# [M] User may override a view's collation and gain unauthorized access to underlying data

## Summary
Severity: Medium
Advisory: BIT-mongodb-2025-3082
Aliases: CVE-2025-3082
Ecosystem: Bitnami
Published: 2025-09-23
Source: https://osv.dev/vulnerability/BIT-mongodb-2025-3082
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=7.3.0 <7.3.4

## Details
A user authorized to access a view may be able to alter the intended collation, allowing them to access to a different or unintended view of underlying data. This issue affects MongoDB Server v5.0 version prior to 5.0.31, MongoDB Server v6.0 version prior to 6.0.20, MongoDB Server v7.0 version prior to 7.0.14 and MongoDB Server v7.3 versions prior to 7.3.4.

## References
- https://jira.mongodb.org/browse/SERVER-103151
- https://nvd.nist.gov/vuln/detail/CVE-2025-3082
