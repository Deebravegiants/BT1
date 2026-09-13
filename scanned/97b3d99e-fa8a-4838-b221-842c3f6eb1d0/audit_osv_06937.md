# [M] Schema validation log messages may not redact user data

## Summary
Severity: Medium
Advisory: BIT-mongodb-2026-8200
Aliases: CVE-2026-8200
Ecosystem: Bitnami
Published: 2026-05-19
Source: https://osv.dev/vulnerability/BIT-mongodb-2026-8200
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=8.3.0 <8.3.2

## Details
When schema validation is enabled on a collection and an update or insert would violate the collection's schema, the local server log message generated may not have all user data redacted. 


This issue impacts MongoDB Server v7.0 versions prior to 7.0.34, v8.0 versions prior to 8.0.23, v8.2 versions prior to 8.2.9 and v8.3 versions prior to 8.3.2.

## References
- https://jira.mongodb.org/browse/SERVER-121895
- https://nvd.nist.gov/vuln/detail/CVE-2026-8200
