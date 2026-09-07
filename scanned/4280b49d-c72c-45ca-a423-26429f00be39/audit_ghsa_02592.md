# [M] Prototype Pollution in open-graph

## Summary
Severity: Medium
Advisory: GHSA-g452-6rfc-vrvx
CVE: CVE-2021-23419
CWE: CWE-1321, CWE-915
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2021-09-01
Source: https://github.com/advisories/GHSA-g452-6rfc-vrvx
Type: github-advisory

## Affected
- npm: `open-graph` — affected >=0 <0.2.6

## Details
This affects the package open-graph before 0.2.6. The function parse could be tricked into adding or modifying properties of Object.prototype using a __proto__ or constructor payload.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23419
- https://github.com/samholmes/node-open-graph/commit/a0cef507a90adaac7dbbe9c404f09a50bdefb348
- https://github.com/samholmes/node-open-graph
- https://snyk.io/vuln/SNYK-JS-OPENGRAPH-1536747
