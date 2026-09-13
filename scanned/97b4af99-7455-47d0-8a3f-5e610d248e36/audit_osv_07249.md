# [H] Parse Server stores password in plain text

## Summary
Severity: High
Advisory: BIT-parse-2020-26288
Aliases: CVE-2020-26288, GHSA-4w46-w44m-3jq3
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-parse-2020-26288
Type: osv

## Affected
- Bitnami: `parse` — affected >=0 <4.5.0

## Details
Parse Server is an open source backend that can be deployed to any infrastructure that can run Node.js. It is an npm package "parse-server". In Parse Server before version 4.5.0, user passwords involved in LDAP authentication are stored in cleartext. This is fixed in version 4.5.0 by stripping password after authentication to prevent cleartext password storage.

## References
- https://github.com/parse-community/parse-server/commit/da905a357d062ab4fea727a21eac231acc2ed92a
- https://github.com/parse-community/parse-server/releases/tag/4.5.0
- https://github.com/parse-community/parse-server/security/advisories/GHSA-4w46-w44m-3jq3
- https://www.npmjs.com/package/parse-server
- https://nvd.nist.gov/vuln/detail/CVE-2020-26288
