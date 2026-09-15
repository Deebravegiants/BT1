# [M] ag-grid packages vulnerable to Prototype Pollution

## Summary
Severity: Medium
Advisory: GHSA-328p-362g-r48j
CVE: CVE-2024-39001
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-07-01
Source: https://github.com/advisories/GHSA-328p-362g-r48j
Type: github-advisory

## Affected
- npm: `@ag-grid-enterprise/charts` — affected >=32.0.0 <32.0.1
- npm: `ag-grid-community` — affected >=32.0.0 <32.0.1
- npm: `ag-grid-enterprise` — affected >=32.0.0 <32.0.1
- npm: `@ag-grid-enterprise/charts` — affected >=0 <31.3.4
- npm: `ag-grid-community` — affected >=0 <31.3.4
- npm: `ag-grid-enterprise` — affected >=0 <31.3.4

## Details
ag-grid-enterprise v31.3.2 was discovered to contain a prototype pollution via the component _ModuleSupport.jsonApply. This vulnerability allows attackers to execute arbitrary code or cause a Denial of Service (DoS) via injecting arbitrary properties.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-39001
- https://github.com/ag-grid/ag-grid/issues/8261
- https://github.com/ag-grid/ag-grid/commit/78fb47f6c996f22c0b7184afb29620ab8c240522
- https://github.com/ag-grid/ag-grid/commit/ff731699453f2632d4852b3a3c34b479c406068c
- https://gist.github.com/mestrtee/18e8c27f3a6376e7cf082cfe1ca766fa
- https://gist.github.com/mestrtee/c1590660750744f25e86ba1bf240844b
- https://gist.github.com/mestrtee/f8037d492dab0d77bca719e05d31c08b
- https://github.com/ag-grid/ag-grid
- https://www.ag-grid.com/changelog/?fixVersion=31.3.4
- https://www.ag-grid.com/changelog/?fixVersion=32.0.1
