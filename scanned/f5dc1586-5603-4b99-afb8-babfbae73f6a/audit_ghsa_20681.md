# [C] heroku-env susceptible to command injection

## Summary
Severity: Critical
Advisory: GHSA-jp45-65jw-94mj
CVE: CVE-2020-28437
CWE: CWE-77
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-08-03
Source: https://github.com/advisories/GHSA-jp45-65jw-94mj
Type: github-advisory

## Affected
- npm: `heroku-env` — affected >=0

## Details
A command injection vulnerability affects all versions of package heroku-env. The injection point is located in lib/get.js which is required by index.js.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-28437
- https://github.com/brianc/node-heroku-env
- https://security.snyk.io/vuln/SNYK-JS-HEROKUENV-1050432
