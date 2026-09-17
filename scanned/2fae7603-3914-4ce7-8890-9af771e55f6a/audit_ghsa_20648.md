# [C] get-npm-package-version Command Injection vulnerability

## Summary
Severity: Critical
Advisory: GHSA-4h66-vghf-xg5x
CVE: CVE-2020-7795
CWE: CWE-77
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-08-03
Source: https://github.com/advisories/GHSA-4h66-vghf-xg5x
Type: github-advisory

## Affected
- npm: `get-npm-package-version` — affected >=0 <1.0.7

## Details
The package get-npm-package-version before 1.0.7 is vulnerable to Command Injection via the `main` function in index.js.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7795
- https://github.com/hoperyy/get-npm-package-version/commit/40b1cf31a0607ea66f9e30a0c3af1383b52b2dec
- https://github.com/hoperyy/get-npm-package-version/commit/49459d4a3ce68587d48ffa8dead86fc9ed58e965
- https://github.com/hoperyy/get-npm-package-version
- https://github.com/hoperyy/get-npm-package-version/blob/338a5882298eb2c2194538db41166cae13c39e03/index.js#L17
- https://security.snyk.io/vuln/SNYK-JS-GETNPMPACKAGEVERSION-1050390
