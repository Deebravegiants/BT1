# [C] exec-local-bin vulnerable to Command Injection

## Summary
Severity: Critical
Advisory: GHSA-f259-h6m8-hm8m
CVE: CVE-2022-25923
CWE: CWE-77, CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-01-06
Source: https://github.com/advisories/GHSA-f259-h6m8-hm8m
Type: github-advisory

## Affected
- npm: `exec-local-bin` — affected >=0 <1.2.0

## Details
Versions of the package exec-local-bin before 1.2.0 are vulnerable to Command Injection via the `theProcess()` functionality due to improper user-input sanitization.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25923
- https://github.com/saeedseyfi/exec-local-bin/commit/d425866375c85038133a6f79db2aac66c0a72624
- https://github.com/saeedseyfi/exec-local-bin
- https://github.com/saeedseyfi/exec-local-bin/blob/92db00bde9d6e2d83410849f898df12f075b73b0/index.js%23L9
- https://security.snyk.io/vuln/SNYK-JS-EXECLOCALBIN-3157956
