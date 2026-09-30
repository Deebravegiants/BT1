# [H] grunt-util-property 0.0.2 function call can add/modify properties of Object.prototype using a __proto__ payload

## Summary
Severity: High
Advisory: GHSA-4hq8-jgr8-mw9j
CVE: CVE-2020-7641
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-07-18
Source: https://github.com/advisories/GHSA-4hq8-jgr8-mw9j
Type: github-advisory

## Affected
- npm: `grunt-util-property` — affected >=0

## Details
This affects all versions of package grunt-util-property. The function call could be tricked into adding or modifying properties of `Object.prototype` using a `__proto__` payload.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7641
- https://github.com/mikaelkaron/grunt-util-property
- https://github.com/mikaelkaron/grunt-util-property/blob/master/main.js%23L41
- https://security.snyk.io/vuln/SNYK-JS-GRUNTUTILPROPERTY-565088
