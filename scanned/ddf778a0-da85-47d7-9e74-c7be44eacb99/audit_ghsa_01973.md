# [H] Prototype Pollution in nedb

## Summary
Severity: High
Advisory: GHSA-339j-hqgx-qrrx
CVE: CVE-2021-23395
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2021-06-21
Source: https://github.com/advisories/GHSA-339j-hqgx-qrrx
Type: github-advisory

## Affected
- npm: `nedb` — affected >=0

## Details
This affects all versions of package nedb. The library could be tricked into adding or modifying properties of Object.prototype using a __proto__ or constructor.prototype payload.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23395
- https://snyk.io/vuln/SNYK-JS-NEDB-1305279
