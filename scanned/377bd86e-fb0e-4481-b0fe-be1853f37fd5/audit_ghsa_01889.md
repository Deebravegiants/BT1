# [H] Uncontrolled Resource Consumption in fun-map

## Summary
Severity: High
Advisory: GHSA-p33m-7w7f-gmj8
CVE: CVE-2020-7644
CWE: CWE-1321, CWE-915
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-12-10
Source: https://github.com/advisories/GHSA-p33m-7w7f-gmj8
Type: github-advisory

## Affected
- npm: `fun-map` — affected >=0

## Details
fun-map through 3.3.1 is vulnerable to Prototype Pollution. The function assocInM could be tricked into adding or modifying properties of 'Object.prototype' using a '__proto__' payload.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7644
- https://github.com/nathan7/fun-map/blob/master/index.js#L137,
- https://snyk.io/vuln/SNYK-JS-FUNMAP-564436
