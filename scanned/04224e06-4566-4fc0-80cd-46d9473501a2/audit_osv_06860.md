# [M] MongoDB Extension for VS Code may unexpectedly store credentials locally in clear text

## Summary
Severity: Medium
Advisory: BIT-mongodb-2021-32039
Aliases: CVE-2021-32039
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mongodb-2021-32039
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=0 <0.7.1

## Details
Users with appropriate file access may be able to access unencrypted user credentials saved by MongoDB Extension for VS Code in a binary file. These credentials may be used by malicious attackers to perform unauthorized actions. This vulnerability affects all MongoDB Extension for VS Code including and prior to version 0.7.0

## References
- https://github.com/mongodb-js/vscode/releases/tag/v0.8.0
- https://jira.mongodb.org/browse/VSCODE-313
- https://nvd.nist.gov/vuln/detail/CVE-2021-32039
