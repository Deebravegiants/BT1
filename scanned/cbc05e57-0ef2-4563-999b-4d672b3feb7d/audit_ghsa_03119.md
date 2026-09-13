# [M] Improperly Controlled Modification of Dynamically-Determined Object Attributes in vega-util

## Summary
Severity: Medium
Advisory: GHSA-6hwh-rqwf-cxxr
CVE: CVE-2019-10806
CWE: CWE-1321, CWE-20, CWE-915
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2021-05-07
Source: https://github.com/advisories/GHSA-6hwh-rqwf-cxxr
Type: github-advisory

## Affected
- npm: `vega-util` — affected >=0 <1.13.1

## Details
vega-util prior to 1.13.1 allows manipulation of object prototype. The &#39;vega.mergeConfig&#39; method within vega-util could be tricked into adding or modifying properties of the Object.prototype.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10806
- https://github.com/vega/vega/commit/8f33a0b5170d7de4f12fc248ec0901234342367b
- https://snyk.io/vuln/SNYK-JS-VEGAUTIL-559223
