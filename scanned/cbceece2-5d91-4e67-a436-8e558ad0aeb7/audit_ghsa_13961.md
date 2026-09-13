# [M] Sequelize information disclosure vulnerability

## Summary
Severity: Medium
Advisory: GHSA-8c25-f3mj-v6h8
CVE: CVE-2023-22580
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-02-16
Source: https://github.com/advisories/GHSA-8c25-f3mj-v6h8
Type: github-advisory

## Affected
- npm: `sequelize` — affected >=0 <6.28.1
- npm: `@sequelize/core` — affected >=0 <7.0.0-alpha.20

## Details
Due to improper input filtering in the sequelize js library, can malicious queries lead to sensitive information disclosure.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-22580
- https://github.com/sequelize/sequelize/pull/15375
- https://github.com/sequelize/sequelize/pull/15699
- https://csirt.divd.nl/CVE-2023-22580
- https://csirt.divd.nl/DIVD-2022-00020
- https://github.com/sequelize/sequelize
- https://github.com/sequelize/sequelize/releases/tag/v6.28.1
- https://github.com/sequelize/sequelize/releases/tag/v7.0.0-alpha.20
