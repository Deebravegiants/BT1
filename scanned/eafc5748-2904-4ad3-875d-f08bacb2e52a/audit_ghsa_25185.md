# [C] Prototype Pollution in convict

## Summary
Severity: Critical
Advisory: GHSA-jjf5-wx3j-3fv7
CVE: CVE-2022-21190
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-jjf5-wx3j-3fv7
Type: github-advisory

## Affected
- npm: `convict` — affected >=0 <6.2.3

## Details
This affects the package convict before 6.2.3. This is a bypass of [CVE-2022-22143](https://security.snyk.io/vuln/SNYK-JS-CONVICT-2340604). The [fix](https://github.com/mozilla/node-convict/commit/3b86be087d8f14681a9c889d45da7fe3ad9cd880) introduced, relies on the startsWith method and does not prevent the vulnerability: before splitting the path, it checks if it starts with __proto__ or this.constructor.prototype. To bypass this check it's possible to prepend the dangerous paths with any string value followed by a dot, like for example foo.__proto__ or foo.this.constructor.prototype.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-21190
- https://github.com/mozilla/node-convict/commit/1ea0ab19c5208f66509e1c43b0d0f21c1fd29b75
- https://gist.github.com/dellalibera/cebce20e51410acebff1f46afdc89808
- https://github.com/mozilla/node-convict
- https://github.com/mozilla/node-convict/blob/3b86be087d8f14681a9c889d45da7fe3ad9cd880/packages/convict/src/main.js%23L571
- https://github.com/mozilla/node-convict/blob/master/CHANGELOG.md%23623---2022-05-07
- https://snyk.io/vuln/SNYK-JS-CONVICT-2774757
