# [M] BIT-mongodb-2024-6384

## Summary
Severity: Medium
Advisory: BIT-mongodb-2024-6384
Aliases: CVE-2024-6384
Ecosystem: Bitnami
Published: 2024-08-17
Source: https://osv.dev/vulnerability/BIT-mongodb-2024-6384
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=7.3.0 <7.3.3

## Details
"Hot" backup files may be downloaded by underprivileged users, if they are capable of acquiring a unique backup identifier. This issue affects MongoDB Enterprise Server v6.0 versions prior to 6.0.16, MongoDB Enterprise Server v7.0 versions prior to 7.0.11 and MongoDB Enterprise Server v7.3 versions prior to 7.3.3

## References
- https://jira.mongodb.org/browse/SERVER-93516
- https://security.netapp.com/advisory/ntap-20241115-0001/
