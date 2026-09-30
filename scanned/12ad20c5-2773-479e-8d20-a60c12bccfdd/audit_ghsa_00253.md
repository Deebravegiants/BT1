# [H] Regular Expression Denial of Service in decamelize

## Summary
Severity: High
Advisory: GHSA-q5c4-39f5-m68j
CVE: CVE-2017-16023
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2018-07-24
Source: https://github.com/advisories/GHSA-q5c4-39f5-m68j
Type: github-advisory

## Affected
- npm: `decamelize` — affected >=1.1.0 <1.1.2

## Details
Affected versions of `decamelize` are susceptible to a denial of service vulnerability when user input is passed directly into `decamelize`.




## Recommendation

Update to version 1.1.2 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16023
- https://github.com/sindresorhus/decamelize/issues/5
- https://github.com/advisories/GHSA-q5c4-39f5-m68j
- https://www.npmjs.com/advisories/308
