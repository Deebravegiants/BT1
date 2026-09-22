# [M] Users could trigger a crash of mongod primaries during promotion to sharded

## Summary
Severity: Medium
Advisory: BIT-mongodb-2026-5170
Aliases: CVE-2026-5170
Ecosystem: Bitnami
Published: 2026-04-06
Source: https://osv.dev/vulnerability/BIT-mongodb-2026-5170
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=8.2.0 <8.2.2

## Details
A user with access to the cluster with a limited set of privilege actions can trigger a crash of a mongod process during the limited and unpredictable window when the cluster is being promoted from a replica set to a sharded cluster. This may cause a denial of service by taking down the primary of the replica set.

This issue affects MongoDB Server v8.2 versions prior to 8.2.2, MongoDB Server v8.0 versions between 8.0.18, MongoDB Server v7.0 versions between 7.0.31.

## References
- https://jira.mongodb.org/browse/SERVER-101758
- https://nvd.nist.gov/vuln/detail/CVE-2026-5170
