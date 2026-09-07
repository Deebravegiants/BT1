# [H] Cross-Site Scripting in jqtree

## Summary
Severity: High
Advisory: GHSA-gjhx-gxwx-jx9j
CVE: CVE-2016-1000234
CWE: CWE-79
Ecosystem: npm
Published: 2020-09-01
Source: https://github.com/advisories/GHSA-gjhx-gxwx-jx9j
Type: github-advisory

## Affected
- npm: `jqtree` — affected >=0 <1.3.4

## Details
Affected versions of `jqtree` are vulnerable to cross-site scripting in the drag and drop functionality for modifying tree data. 

When a user attempts to drag a node to a different position in the hierarchy, script content existing within the node will be executed.


## Recommendation

Update to 1.3.4 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-1000234
- https://github.com/mbraak/jqTree/issues/437
- https://github.com/mbraak/jqTree
- https://www.npmjs.com/advisories/132
