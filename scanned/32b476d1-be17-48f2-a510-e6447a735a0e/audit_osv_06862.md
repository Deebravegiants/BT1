# [M] MongoDB Server (mongod) may crash in response to unexpected requests

## Summary
Severity: Medium
Advisory: BIT-mongodb-2022-24272
Aliases: CVE-2022-24272
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mongodb-2022-24272
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=5.0.0 <5.0.7

## Details
An authenticated user may trigger an invariant assertion during command dispatch due to incorrect validation on the $external database. This may result in mongod denial of service or server crash. This issue affects: MongoDB Inc. MongoDB Server v5.0 versions, prior to and including v5.0.6.

## References
- https://jira.mongodb.org/browse/SERVER-63968
- https://nvd.nist.gov/vuln/detail/CVE-2022-24272
