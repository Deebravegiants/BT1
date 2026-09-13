# [H] Prototype pollution in ag-grid-community via the _.mergeDeep function

## Summary
Severity: High
Advisory: GHSA-876p-c77m-x2hc
CVE: CVE-2024-38996
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-07-01
Source: https://github.com/advisories/GHSA-876p-c77m-x2hc
Type: github-advisory

## Affected
- npm: `ag-grid-enterprise` — affected >=0 <31.3.4
- npm: `ag-grid-community` — affected >=0 <31.3.4

## Details
ag-grid-community v31.3.2 and ag-grid-enterprise v31.3.2 were discovered to contain a prototype pollution via the _.mergeDeep function. This vulnerability allows attackers to execute arbitrary code or cause a Denial of Service (DoS) via injecting arbitrary properties. Prior versions were also found to be affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-38996
- https://github.com/ag-grid/ag-grid/pull/8290
- https://gist.github.com/mestrtee/18e8c27f3a6376e7cf082cfe1ca766fa
- https://gist.github.com/mestrtee/c1590660750744f25e86ba1bf240844b
- https://gist.github.com/mestrtee/f8037d492dab0d77bca719e05d31c08b
- https://github.com/ag-grid/ag-grid
