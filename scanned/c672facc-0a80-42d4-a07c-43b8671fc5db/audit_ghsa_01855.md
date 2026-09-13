# [C] Command Injection in compass-compile

## Summary
Severity: Critical
Advisory: GHSA-7q9f-x6rm-qmxr
CVE: CVE-2020-7635
CWE: CWE-74
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-12-09
Source: https://github.com/advisories/GHSA-7q9f-x6rm-qmxr
Type: github-advisory

## Affected
- npm: `compass-compile` — affected >=0

## Details
compass-compile through 0.0.1 is vulnerable to Command Injection. It allows execution of arbitrary commands via the options argument.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7635
- https://github.com/quaertym/compass-compile
- https://github.com/quaertym/compass-compile/blob/master/lib/compass.js#L25
- https://snyk.io/vuln/SNYK-JS-COMPASSCOMPILE-564429
