# [M] MongoDB Server secondaries may crash due to forced index constraints

## Summary
Severity: Medium
Advisory: BIT-mongodb-2024-8305
Aliases: CVE-2024-8305
Ecosystem: Bitnami
Published: 2024-11-08
Source: https://osv.dev/vulnerability/BIT-mongodb-2024-8305
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=7.0.0 <7.0.14

## Details
prepareUnique index may cause secondaries to crash due to incorrect enforcement of index constraints on secondaries, where in extreme cases may cause multiple secondaries crashing leading to no primaries. This issue affects MongoDB Server v6.0 versions prior to 6.0.17, MongoDB Server v7.0 versions prior to 7.0.13 and MongoDB Server v7.3 versions prior to 7.3.4

## References
- https://jira.mongodb.org/browse/SERVER-92382
- https://nvd.nist.gov/vuln/detail/CVE-2024-8305
