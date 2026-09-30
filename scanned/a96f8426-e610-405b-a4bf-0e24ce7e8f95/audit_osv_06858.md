# [H] Denial of Service and Data Integrity vulnerability in features command

## Summary
Severity: High
Advisory: BIT-mongodb-2021-32036
Aliases: CVE-2021-32036
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mongodb-2021-32036
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=5.0.0 <5.0.4

## Details
An authenticated user without any specific authorizations may be able to repeatedly invoke the features command where at a high volume may lead to resource depletion or generate high lock contention. This may result in denial of service and in rare cases could result in id field collisions. This issue affects MongoDB Server v5.0 versions prior to and including 5.0.3; MongoDB Server v4.4 versions prior to and including 4.4.9; MongoDB Server v4.2 versions prior to and including 4.2.16 and MongoDB Server v4.0 versions prior to and including 4.0.28

## References
- https://jira.mongodb.org/browse/SERVER-59294
- https://nvd.nist.gov/vuln/detail/CVE-2021-32036
