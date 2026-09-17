# [M] Directory Traversal in nhouston

## Summary
Severity: Medium
Advisory: GHSA-44g9-w23c-5rw7
CVE: CVE-2014-8883
CWE: CWE-23
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2020-08-31
Source: https://github.com/advisories/GHSA-44g9-w23c-5rw7
Type: github-advisory

## Affected
- npm: `nhouston` — affected >=0.0.0

## Details
All versions of the static file server module nhouston are vulnerable to directory traversal. An attacker can provide input such as `../` to read files outside of the served directory.


## Recommendation

It is recommended that a different module be used, as we have been unable to reacher the maintainer of this module. We will continue to reach out to them, and if an update becomes available that fixes the issue, we will update this advisory accordingly.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-8883
- https://snyk.io/vuln/npm:nhouston:20141114
- https://www.npmjs.com/advisories/25
- http://en.wikipedia.org/wiki/Directory_traversal_attack
