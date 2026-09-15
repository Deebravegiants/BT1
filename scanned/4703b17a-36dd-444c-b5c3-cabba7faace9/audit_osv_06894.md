# [M] Incomplete Redaction of Sensitive Information in MongoDB Server Logs

## Summary
Severity: Medium
Advisory: BIT-mongodb-2025-6711
Aliases: CVE-2025-6711
Ecosystem: Bitnami
Published: 2025-10-05
Source: https://osv.dev/vulnerability/BIT-mongodb-2025-6711
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=8.0.0 <8.0.5

## Details
An issue has been identified in MongoDB Server where unredacted queries may inadvertently appear in server logs when certain error conditions are encountered. This issue affects MongoDB Server v8.0 versions prior to 8.0.5, MongoDB Server v7.0 versions prior to 7.0.18 and MongoDB Server v6.0 versions prior to 6.0.21.

## References
- https://jira.mongodb.org/browse/SERVER-98720
- https://nvd.nist.gov/vuln/detail/CVE-2025-6711
