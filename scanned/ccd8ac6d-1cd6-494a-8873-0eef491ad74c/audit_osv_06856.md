# [M] Specific replication command with malformed oplog entries can crash secondaries

## Summary
Severity: Medium
Advisory: BIT-mongodb-2021-20330
Aliases: CVE-2021-20330
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mongodb-2021-20330
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=4.4.0 <4.4.6

## Details
An attacker with basic CRUD permissions on a replicated collection can run the applyOps command with specially malformed oplog entries, resulting in a potential denial of service on secondaries. This issue affects MongoDB Server v4.0 versions prior to 4.0.27; MongoDB Server v4.2 versions prior to 4.2.16; MongoDB Server v4.4 versions prior to 4.4.9.

## References
- https://jira.mongodb.org/browse/SERVER-36263
- https://nvd.nist.gov/vuln/detail/CVE-2021-20330
