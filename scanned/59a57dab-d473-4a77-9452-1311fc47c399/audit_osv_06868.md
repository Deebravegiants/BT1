# [M] Missing authorization check may lead to shard key refinement

## Summary
Severity: Medium
Advisory: BIT-mongodb-2024-6375
Aliases: CVE-2024-6375
Ecosystem: Bitnami
Published: 2024-07-04
Source: https://osv.dev/vulnerability/BIT-mongodb-2024-6375
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=7.0.0 <7.0.3

## Details
A command for refining a collection shard key is missing an authorization check. This may cause the command to run directly on a shard, leading to either degradation of query performance, or to revealing chunk boundaries through timing side channels. This affects MongoDB Server v5.0 versions, prior to 5.0.22, MongoDB Server v6.0 versions, prior to 6.0.11 and MongoDB Server v7.0 versions prior to 7.0.3.

## References
- https://jira.mongodb.org/browse/SERVER-79327
- https://nvd.nist.gov/vuln/detail/CVE-2024-6375
