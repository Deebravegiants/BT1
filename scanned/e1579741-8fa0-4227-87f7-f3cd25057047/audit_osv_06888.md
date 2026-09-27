# [M] MongoDB Server may crash due to improper validation of explain command

## Summary
Severity: Medium
Advisory: BIT-mongodb-2025-3084
Aliases: CVE-2025-3084
Ecosystem: Bitnami
Published: 2025-09-25
Source: https://osv.dev/vulnerability/BIT-mongodb-2025-3084
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=8.0.0 <8.0.4

## Details
When run on commands with certain arguments set, explain may fail to validate these arguments before using them. This can lead to crashes in router servers. This affects MongoDB Server v5.0 prior to 5.0.31, MongoDB Server v6.0 prior to 6.0.20, MongoDB Server v7.0 prior to 7.0.16 and MongoDB Server v8.0 prior to 8.0.4

## References
- https://jira.mongodb.org/browse/SERVER-103153
- https://nvd.nist.gov/vuln/detail/CVE-2025-3084
