# [H] steal Inefficient Regular Expression Complexity vulnerability via string variable

## Summary
Severity: High
Advisory: GHSA-rgqx-226f-2xp4
CVE: CVE-2022-37259
CWE: CWE-1333
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-09-21
Source: https://github.com/advisories/GHSA-rgqx-226f-2xp4
Type: github-advisory

## Affected
- npm: `steal` — affected >=0

## Details
A Regular Expression Denial of Service (ReDoS) flaw was found in stealjs steal 2.2.4 via the string variable in babel.js.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-37259
- https://github.com/stealjs/steal/issues/1528
- https://github.com/stealjs/steal
- https://github.com/stealjs/steal/blob/c9dd1eb19ed3f97aeb93cf9dcea5d68ad5d0ced9/ext/babel.js#L54124
- https://github.com/stealjs/steal/blob/c9dd1eb19ed3f97aeb93cf9dcea5d68ad5d0ced9/ext/babel.js#L54129
