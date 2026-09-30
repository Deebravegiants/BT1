# [H] Time-series operations may cause internal BSON size limit to be exceed

## Summary
Severity: High
Advisory: BIT-mongodb-2025-13507
Aliases: CVE-2025-13507
Ecosystem: Bitnami
Published: 2025-12-06
Source: https://osv.dev/vulnerability/BIT-mongodb-2025-13507
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=8.2.0 <8.2.1

## Details
Inconsistent object size validation in time series processing logic may result in later processing of oversized BSON documents leading to an assert failing and process termination. 
This issue impacts MongoDB Server v7.0 versions prior to 7.0.26, v8.0 versions prior to 8.0.16 and MongoDB server v8.2 versions prior to 8.2.1.

## References
- https://jira.mongodb.org/browse/SERVER-108565
- https://nvd.nist.gov/vuln/detail/CVE-2025-13507
