# [C] OS Command Injection in gulp-scss-lint

## Summary
Severity: Critical
Advisory: GHSA-g4hj-r7r3-9rwv
CVE: CVE-2020-7601
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-05-07
Source: https://github.com/advisories/GHSA-g4hj-r7r3-9rwv
Type: github-advisory

## Affected
- npm: `gulp-scss-lint` — affected >=0

## Details
gulp-scss-lint through 1.0.0 allows execution of arbitrary commands. It is possible to inject arbitrary commands to the &quot;exec&quot; function located in &quot;src/command.js&quot; via the provided options.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7601
- https://snyk.io/vuln/SNYK-JS-GULPSCSSLINT-560114
