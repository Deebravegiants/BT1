# [C] Command injection in ts-process-promises

## Summary
Severity: Critical
Advisory: GHSA-ww4j-c2rq-47q8
CVE: CVE-2020-7784
CWE: CWE-77
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-01-13
Source: https://github.com/advisories/GHSA-ww4j-c2rq-47q8
Type: github-advisory

## Affected
- npm: `ts-process-promises` — affected 1.0.2

## Details
This affects all versions of package ts-process-promises. The injection point is located in line 45 in main entry of package in lib/process-promises.js.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7784
- https://snyk.io/vuln/SNYK-JS-TSPROCESSPROMISES-1048334
