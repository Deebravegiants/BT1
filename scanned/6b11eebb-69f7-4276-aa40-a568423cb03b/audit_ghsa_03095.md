# [H] Path Traversal in marked-tree

## Summary
Severity: High
Advisory: GHSA-xr8h-53xr-jhcm
CVE: CVE-2020-7682
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-05-07
Source: https://github.com/advisories/GHSA-xr8h-53xr-jhcm
Type: github-advisory

## Affected
- npm: `marked-tree` — affected >=0

## Details
This affects all versions up to and including version 0.8.1 of package marked-tree. There is no path sanitization in the path provided at fs.readFile in index.js.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7682
- https://snyk.io/vuln/SNYK-JS-MARKEDTREE-590121
