# [M] json-2-csv vulnerable to CSV Injection via the preventCsvInjection optio

## Summary
Severity: Medium
Advisory: GHSA-g27c-q7cp-mhx6
CVE: CVE-2026-9673
CWE: CWE-1236
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-05-28
Source: https://github.com/advisories/GHSA-g27c-q7cp-mhx6
Type: github-advisory

## Affected
- npm: `json-2-csv` — affected >=3.15.0 <5.5.11

## Details
Versions of the package json-2-csv from 3.15.0 and before 5.5.11 are vulnerable to CSV Injection via the preventCsvInjection option which can be bypassed. An attacker can inject formulas into CSV files, which execute when the files are opened in spreadsheet applications.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-9673
- https://github.com/mrodrig/json-2-csv/commit/0fdd0bb6d0273178cd940afc323ccbce19688229
- https://gist.github.com/whoamins/299745a2d36b482b44e9613b78e40613
- https://github.com/mrodrig/json-2-csv
- https://github.com/mrodrig/json-2-csv/blob/main/src/json2csv.ts%23L410
- https://security.snyk.io/vuln/SNYK-JS-JSON2CSV-14221326
