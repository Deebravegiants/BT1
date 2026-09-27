# [M] Specific GeoQuery can cause DoS against MongoDB Server

## Summary
Severity: Medium
Advisory: BIT-mongodb-2020-7923
Aliases: CVE-2020-7923
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mongodb-2020-7923
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=4.4.0 <4.4.0

## Details
A user authorized to perform database queries may cause denial of service by issuing specially crafted queries, which violate an invariant in the query subsystem's support for geoNear. This issue affects MongoDB Server v4.4 versions prior to 4.4.0; MongoDB Server v4.2 versions prior to 4.2.8 and MongoDB Server v4.0 versions prior to 4.0.19.

## References
- https://jira.mongodb.org/browse/SERVER-47773
- https://nvd.nist.gov/vuln/detail/CVE-2020-7923
