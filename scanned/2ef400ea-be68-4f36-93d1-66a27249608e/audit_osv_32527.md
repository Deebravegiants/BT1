# [H] CVE-2025-3193

## Summary
Severity: High
Advisory: CVE-2025-3193
Aliases: GHSA-529q-4j3p-7c5r
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-27
Source: https://osv.dev/vulnerability/CVE-2025-3193
Type: osv

## Details
Versions of the package algoliasearch-helper from 2.0.0-rc1 and before 3.11.2 are vulnerable to Prototype Pollution in the _merge() function in merge.js, which allows constructor.prototype to be written even though doing so throws an error. In the "extreme edge-case" that the resulting error is caught, code injected into the user-supplied search parameter may be exeucted.This is related to but distinct from the issue reported in [CVE-2021-23433](https://security.snyk.io/vuln/SNYK-JS-ALGOLIASEARCHHELPER-1570421).**NOTE:** This vulnerability is not exploitable in the default configuration of InstantSearch since searchParameters are not modifiable by users.

## References
- https://security.snyk.io/vuln/SNYK-JS-ALGOLIASEARCHHELPER-3318396
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/3xxx/CVE-2025-3193.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-3193
- https://github.com/algolia/algoliasearch-helper-js/issues/922
- https://github.com/algolia/algoliasearch-helper-js/commit/776dff23c87b0902e554e02a8c2567d2580fe12a
