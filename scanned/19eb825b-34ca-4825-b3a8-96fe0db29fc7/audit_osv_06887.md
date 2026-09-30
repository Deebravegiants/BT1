# [H] Malformed MongoDB wire protocol messages may cause mongos to crash

## Summary
Severity: High
Advisory: BIT-mongodb-2025-3083
Aliases: CVE-2025-3083
Ecosystem: Bitnami
Published: 2025-09-23
Source: https://osv.dev/vulnerability/BIT-mongodb-2025-3083
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=7.0.0 <7.0.16

## Details
Specifically crafted MongoDB wire protocol messages can cause mongos to crash during command validation. This can occur without using an authenticated connection. This issue affects MongoDB v5.0 versions prior to 5.0.31,  MongoDB v6.0 versions prior to 6.0.20 and MongoDB v7.0 versions prior to 7.0.16

## References
- https://jira.mongodb.org/browse/SERVER-103152
- https://nvd.nist.gov/vuln/detail/CVE-2025-3083
