# [M] Administrative action may disable enforcement of per-user IP whitelisting

## Summary
Severity: Medium
Advisory: BIT-mongodb-2020-7921
Aliases: CVE-2020-7921
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mongodb-2020-7921
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=4.3.0 <4.3.3

## Details
Improper serialization of internal state in the authorization subsystem in MongoDB Server's authorization subsystem permits a user with valid credentials to bypass IP whitelisting protection mechanisms following administrative action. This issue affects MongoDB Server v4.2 versions prior to 4.2.3; MongoDB Server v4.0 versions prior to 4.0.15; MongoDB Server v4.3 versions prior to 4.3.3and MongoDB Server v3.6 versions prior to 3.6.18.

## References
- https://jira.mongodb.org/browse/SERVER-45472
- https://nvd.nist.gov/vuln/detail/CVE-2020-7921
