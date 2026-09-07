# [C] OS Command Injection in gulp-tape

## Summary
Severity: Critical
Advisory: GHSA-x67x-98x7-wv26
CVE: CVE-2020-7605
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-05-07
Source: https://github.com/advisories/GHSA-x67x-98x7-wv26
Type: github-advisory

## Affected
- npm: `gulp-tape` — affected >=0

## Details
gulp-tape through 1.0.0 allows execution of arbitrary commands. It is possible to inject arbitrary commands as part of `gulp-tape` options.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7605
- https://snyk.io/vuln/SNYK-JS-GULPTAPE-560124
