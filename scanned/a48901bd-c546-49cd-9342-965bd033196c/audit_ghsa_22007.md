# [M] Prototype Pollution in dot-object

## Summary
Severity: Medium
Advisory: GHSA-j9cf-pr2x-5273
CVE: CVE-2019-10793
CWE: CWE-74
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2022-02-09
Source: https://github.com/advisories/GHSA-j9cf-pr2x-5273
Type: github-advisory

## Affected
- npm: `dot-object` — affected >=0 <2.1.3

## Details
dot-object before 2.1.3 is vulnerable to Prototype Pollution. The set function could be tricked into adding or modifying properties of Object.prototype using a __proto__ payload.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10793
- https://github.com/rhalff/dot-object/commit/f76cff5fe6d01d30ce110d8f454db2e5bd28a7de
- https://github.com/rhalff/dot-object
- https://snyk.io/vuln/SNYK-JS-DOTOBJECT-548905
