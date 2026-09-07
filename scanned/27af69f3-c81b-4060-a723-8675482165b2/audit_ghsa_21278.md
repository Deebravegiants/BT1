# [C] feathers-sequelize vulnerable to SQL injection due to improper parameter filtering

## Summary
Severity: Critical
Advisory: GHSA-5hq7-j5wq-p227
CVE: CVE-2022-29822
CWE: CWE-89
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-10-26
Source: https://github.com/advisories/GHSA-5hq7-j5wq-p227
Type: github-advisory

## Affected
- npm: `feathers-sequelize` — affected >=6.0.0 <6.3.4

## Details
feathers-sequelize is vulnerable to improper parameter filtering in the Feathers js library, which may ultimately lead to SQL injection.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-29822
- https://github.com/feathersjs-ecosystem/feathers-sequelize/commit/0f2d85f0b2d556f2b6c70423dcebdbd29d95e3dc
- https://csirt.divd.nl/CVE-2022-29822
- https://csirt.divd.nl/DIVD-2022-00020
- https://csirt.divd.nl/cases/DIVD-2022-00020
- https://csirt.divd.nl/cves/CVE-2022-29822
- https://github.com/feathersjs-ecosystem/feathers-sequelize
