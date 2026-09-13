# [C] Prototype Pollution in algoliasearch-helper

## Summary
Severity: Critical
Advisory: GHSA-vpf5-82c8-9v36
CVE: CVE-2021-23433
CWE: CWE-1321, CWE-915
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-11-23
Source: https://github.com/advisories/GHSA-vpf5-82c8-9v36
Type: github-advisory

## Affected
- npm: `algoliasearch-helper` — affected >=0 <3.6.2

## Details
The package algoliasearch-helper before 3.6.2 are vulnerable to Prototype Pollution due to use of the merge function in src/SearchParameters/index.jsSearchParameters._parseNumbers without any protection against prototype properties. Note that this vulnerability is only exploitable if the implementation allows users to define arbitrary search patterns.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23433
- https://github.com/algolia/algoliasearch-helper-js/commit/4ff542b70b92a6b81cce8b9255700b0bc0817edd
- https://github.com/algolia/algoliasearch-helper-js
- https://github.com/algolia/algoliasearch-helper-js/blob/3.5.5/src/SearchParameters/index.js%23L291
- https://snyk.io/vuln/SNYK-JS-ALGOLIASEARCHHELPER-1570421
