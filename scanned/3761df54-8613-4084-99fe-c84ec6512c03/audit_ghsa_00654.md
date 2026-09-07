# [C] Command injection in connection-tester

## Summary
Severity: Critical
Advisory: GHSA-w5mp-8p8w-mhh8
CVE: CVE-2020-7781
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-12-17
Source: https://github.com/advisories/GHSA-w5mp-8p8w-mhh8
Type: github-advisory

## Affected
- npm: `connection-tester` — affected >=0 <0.2.1

## Details
This affects the package connection-tester before 0.2.1. The injection point is located in line 15 in index.js. Affected versions of this package are vulnerable to Command Injection

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7781
- https://github.com/skoranga/node-connection-tester/pull/10
- https://snyk.io/vuln/SNYK-JS-CONNECTIONTESTER-1048337
