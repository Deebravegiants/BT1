# [C] sonar-wrapper Command Injection vulnerability

## Summary
Severity: Critical
Advisory: GHSA-wr4v-3f2h-6hhh
CVE: CVE-2020-28443
CWE: CWE-77
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-07-26
Source: https://github.com/advisories/GHSA-wr4v-3f2h-6hhh
Type: github-advisory

## Affected
- npm: `sonar-wrapper` — affected >=0

## Details
A command injection vulnerability affects all versions of package sonar-wrapper. The injection point is located in lib/sonarRunner.js.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-28443
- https://github.com/llooiicc/sonar-wrapper
- https://github.com/llooiicc/sonar-wrapper/blob/master/lib/sonarRunner.js
- https://security.snyk.io/vuln/SNYK-JS-SONARWRAPPER-1050980
