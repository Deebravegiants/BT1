# [M] MongoDB Server router will crash when incorrect lsid is set on a sharded query

## Summary
Severity: Medium
Advisory: BIT-mongodb-2025-10059
Aliases: CVE-2025-10059
Ecosystem: Bitnami
Published: 2025-09-23
Source: https://osv.dev/vulnerability/BIT-mongodb-2025-10059
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=8.0.0 <8.0.6

## Details
An improper setting of the lsid field on any sharded query can cause a crash in MongoDB routers. This issue occurs when a generic argument (lsid) is provided in a case when it is not applicable. This affects MongoDB Server v6.0 versions prior to 6.0.x, MongoDB Server v7.0 versions prior to 7.0.18 and MongoDB Server v8.0 versions prior to 8.0.6.

## References
- https://jira.mongodb.org/browse/SERVER-100901
- https://jira.mongodb.org/browse/SERVER-100909
- https://nvd.nist.gov/vuln/detail/CVE-2025-10059
