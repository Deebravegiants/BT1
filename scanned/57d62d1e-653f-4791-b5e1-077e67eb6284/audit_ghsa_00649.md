# [M] Code Injection in mquery

## Summary
Severity: Medium
Advisory: GHSA-45q2-34rf-mr94
CVE: CVE-2020-35149
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2020-12-18
Source: https://github.com/advisories/GHSA-45q2-34rf-mr94
Type: github-advisory

## Affected
- npm: `mquery` — affected >=0 <3.2.3

## Details
lib/utils.js in mquery before 3.2.3 allows a pollution attack because a special property (e.g., __proto__) can be copied during a merge or clone operation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-35149
- https://github.com/aheckmann/mquery/commit/792e69fd0a7281a0300be5cade5a6d7c1d468ad4
