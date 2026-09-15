# [M] MongoDB Server may allow queries to be terminated by unauthorized users

## Summary
Severity: Medium
Advisory: BIT-mongodb-2025-13643
Aliases: CVE-2025-13643
Ecosystem: Bitnami
Published: 2025-12-12
Source: https://osv.dev/vulnerability/BIT-mongodb-2025-13643
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=8.0.0 <8.0.14

## Details
A user with access to the cluster with a limited set of privilege actions may be able to terminate queries that are being executed by other users. This may cause a denial of service by preventing a fraction of queries from successfully completing. This issue affects MongoDB Server v7.0 versions prior to 7.0.26 and MongoDB Server v8.0 versions prior to 8.0.14

## References
- https://jira.mongodb.org/browse/SERVER-103582
- https://nvd.nist.gov/vuln/detail/CVE-2025-13643
