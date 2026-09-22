# [H] Validation Bypass in kind-of

## Summary
Severity: High
Advisory: GHSA-6c8f-qphg-qjgp
CVE: CVE-2019-20149
CWE: CWE-668
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2020-03-31
Source: https://github.com/advisories/GHSA-6c8f-qphg-qjgp
Type: github-advisory

## Affected
- npm: `kind-of` — affected >=6.0.0 <6.0.3

## Details
Versions of `kind-of` 6.x prior to 6.0.3 are vulnerable to a Validation Bypass. A maliciously crafted object can alter the result of the type check, allowing attackers to bypass the type checking validation. 


## Recommendation

Upgrade to versions 6.0.3 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-20149
- https://github.com/jonschlinkert/kind-of/issues/30
- https://github.com/jonschlinkert/kind-of/pull/31
- https://github.com/jonschlinkert/kind-of/commit/1df992ce6d5a1292048e5fe9c52c5382f941ee0b
- https://snyk.io/vuln/SNYK-JS-KINDOF-537849
- https://www.npmjs.com/advisories/1490
