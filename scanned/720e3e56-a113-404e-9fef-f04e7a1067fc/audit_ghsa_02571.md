# [H] Prototype Pollution in cookiex/deep

## Summary
Severity: High
Advisory: GHSA-92v9-xh2q-fq9f
CVE: CVE-2021-23442
CWE: CWE-1321, CWE-915
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2021-09-20
Source: https://github.com/advisories/GHSA-92v9-xh2q-fq9f
Type: github-advisory

## Affected
- npm: `@cookiex/deep` — affected >=0 <0.0.7

## Details
The npm @cookiex/deep package before version 0.0.7 has a prototype pollution vulnerability. The global proto object can be polluted using the __proto__ object.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23442
- https://github.com/tony-tsx/cookiex-deep/issues/1
- https://github.com/tony-tsx/cookiex-deep/commit/b5bea2b7f34a5fa9abb4446cbd038ecdbcd09c88
- https://github.com/tony-tsx/cookiex-deep
- https://snyk.io/vuln/SNYK-JS-COOKIEXDEEP-1582793
