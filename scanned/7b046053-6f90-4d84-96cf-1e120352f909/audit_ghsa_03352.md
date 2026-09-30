# [C] OS Command Injection in giting

## Summary
Severity: Critical
Advisory: GHSA-53xj-v576-3ch2
CVE: CVE-2019-10802
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-04-13
Source: https://github.com/advisories/GHSA-53xj-v576-3ch2
Type: github-advisory

## Affected
- npm: `giting` — affected >=0

## Details
giting version prior to 0.0.8 allows execution of arbritary commands. The first argument `repo` of function `pull()` is executed by the package without any validation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10802
- https://github.com/MangoRaft/git
- https://snyk.io/vuln/SNYK-JS-GITING-559008
- https://web.archive.org/web/20201208120654/https://github.com/MangoRaft/git/commit/9be41081f547d3dcef25e7d7c957bc2a3be2dfe0
