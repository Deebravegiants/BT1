# [H] MongoDB Server may be susceptible to privilege escalation due to $mergeCursors stage

## Summary
Severity: High
Advisory: BIT-mongodb-2025-6713
Aliases: CVE-2025-6713
Ecosystem: Bitnami
Published: 2025-10-05
Source: https://osv.dev/vulnerability/BIT-mongodb-2025-6713
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=8.0.0 <8.0.7

## Details
An unauthorized user may leverage a specially crafted aggregation pipeline to access data without proper authorization due to improper handling of the $mergeCursors stage in MongoDB Server. This may lead to access to data without further authorisation. This issue affects MongoDB Server MongoDB Server v8.0 versions prior to 8.0.7, MongoDB Server v7.0 versions prior to 7.0.19 and MongoDB Server v6.0 versions prior to 6.0.22

## References
- https://jira.mongodb.org/browse/SERVER-106752
- https://nvd.nist.gov/vuln/detail/CVE-2025-6713
