# [M] jSuites subect to Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-r4hg-4cpq-q57c
CVE: CVE-2022-25979
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-01-31
Source: https://github.com/advisories/GHSA-r4hg-4cpq-q57c
Type: github-advisory

## Affected
- npm: `jsuites` — affected >=0 <5.0.1

## Details
Versions of the package jsuites before 5.0.1 are vulnerable to Cross-site Scripting (XSS) due to improper user-input sanitization in the Editor() function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25979
- https://github.com/jsuites/jsuites/issues/134
- https://github.com/jsuites/jsuites/commit/b31770d5fe91684a00177f629aab933139c32d9f
- https://github.com/jsuites/jsuites
- https://security.snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-3253331
- https://security.snyk.io/vuln/SNYK-JS-JSUITES-3226764
