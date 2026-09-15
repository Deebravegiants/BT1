# [C] Feather-Sequelize cleanQuery method vulnerable to Prototype Pollution

## Summary
Severity: Critical
Advisory: GHSA-p5m3-27vh-52j4
CVE: CVE-2022-29823
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-10-26
Source: https://github.com/advisories/GHSA-p5m3-27vh-52j4
Type: github-advisory

## Affected
- npm: `feathers-sequelize` — affected >=6.0.0 <6.3.3

## Details
Feather-Sequelize cleanQuery method uses insecure recursive logic to filter unsupported keys from the query object. This results in a Remote Code Execution (RCE) with privileges of application.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-29823
- https://github.com/feathersjs-ecosystem/feathers-sequelize/commit/0b7beaa773dc313fdb27edd9ee8115064d7cf114
- https://csirt.divd.nl/CVE-2022-29823
- https://csirt.divd.nl/DIVD-2022-00020
- https://csirt.divd.nl/cases/DIVD-2022-00020
- https://csirt.divd.nl/cves/CVE-2022-29823
- https://github.com/feathersjs-ecosystem/feathers-sequelize
