# [M] Server log entry spoofing via newline injection

## Summary
Severity: Medium
Advisory: BIT-mongodb-2021-20333
Aliases: CVE-2021-20333
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mongodb-2021-20333
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=4.2.0 <4.2.10

## Details
Sending specially crafted commands to a MongoDB Server may result in artificial log entries being generated or for log entries to be split. This issue affects MongoDB Server v3.6 versions prior to 3.6.20; MongoDB Server v4.0 versions prior to 4.0.21 and MongoDB Server v4.2 versions prior to 4.2.10.

## References
- https://jira.mongodb.org/browse/SERVER-50605
- https://nvd.nist.gov/vuln/detail/CVE-2021-20333
