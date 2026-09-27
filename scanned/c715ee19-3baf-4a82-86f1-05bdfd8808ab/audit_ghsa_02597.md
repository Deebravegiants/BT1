# [M] Denial of Service in node-static

## Summary
Severity: Medium
Advisory: GHSA-8r4g-cg4m-x23c
CWE: CWE-248, CWE-400
Ecosystem: npm
Published: 2021-09-22
Source: https://github.com/advisories/GHSA-8r4g-cg4m-x23c
Type: github-advisory

## Affected
- npm: `node-static` — affected >=0

## Details
All versions of node-static are vulnerable to a Denial of Service. The package fails to catch an exception when user input includes null bytes. This allows attackers to access `http://host/%00` and crash the server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-11149
- https://github.com/cloudhead/node-static/pull/213
- https://github.com/github/advisory-database/pull/6248
- https://github.com/cloudhead/node-static
- https://github.com/cloudhead/node-static/blob/643a528ec7bbd05a59c4030655d94810570afb3f/CHANGES.md#-unreleased
- https://security.snyk.io/vuln/SNYK-JS-NODESTATIC-1297183
