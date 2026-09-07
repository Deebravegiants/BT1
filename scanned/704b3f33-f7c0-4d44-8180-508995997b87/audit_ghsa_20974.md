# [C] steal vulnerable to Prototype Pollution

## Summary
Severity: Critical
Advisory: GHSA-gvjw-8mmr-8f6g
CVE: CVE-2022-37258
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-09-17
Source: https://github.com/advisories/GHSA-gvjw-8mmr-8f6g
Type: github-advisory

## Affected
- npm: `steal` — affected >=0

## Details
Prototype pollution vulnerability in function convertLater in npm-convert.js in stealjs steal 2.2.4 via the packageName variable in npm-convert.js.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-37258
- https://github.com/stealjs/steal/issues/1527
- https://github.com/stealjs/steal
- https://github.com/stealjs/steal/blob/c9dd1eb19ed3f97aeb93cf9dcea5d68ad5d0ced9/ext/npm-convert.js#L362
- https://github.com/stealjs/steal/blob/c9dd1eb19ed3f97aeb93cf9dcea5d68ad5d0ced9/ext/npm-convert.js#L369
