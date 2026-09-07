# [M] Uncontrolled Resource Consumption in rdf-graph-array

## Summary
Severity: Medium
Advisory: GHSA-prv2-xwr7-hr57
CVE: CVE-2019-10798
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2021-04-13
Source: https://github.com/advisories/GHSA-prv2-xwr7-hr57
Type: github-advisory

## Affected
- npm: `rdf-graph-array` — affected >=0

## Details
rdf-graph-array through 0.3.0-rc6 manipulation of JavaScript objects resutling in Prototype Pollution. The rdf.Graph.prototype.add method could be tricked into adding or modifying properties of Object.prototype.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10798
- https://github.com/rdf-ext-archive/rdf-graph-array/blob/master/index.js#L211
- https://snyk.io/vuln/SNYK-JS-RDFGRAPHARRAY-551803
