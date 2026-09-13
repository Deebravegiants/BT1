# [H] Code Injection in mosc

## Summary
Severity: High
Advisory: GHSA-j665-rvj7-2jv9
CVE: CVE-2020-7672
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2021-05-17
Source: https://github.com/advisories/GHSA-j665-rvj7-2jv9
Type: github-advisory

## Affected
- npm: `mosc` — affected >=0

## Details
mosc through 1.0.0 is vulnerable to Arbitrary Code Execution. User input provided to `properties` argument is executed by the `eval` function, resulting in code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7672
- https://snyk.io/vuln/SNYK-JS-MOSC-571492
