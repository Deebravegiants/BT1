# [H] Prototype Pollution in mathjs

## Summary
Severity: High
Advisory: GHSA-x2fc-mxcx-w4mf
CVE: CVE-2020-7743
CWE: CWE-915
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2021-05-10
Source: https://github.com/advisories/GHSA-x2fc-mxcx-w4mf
Type: github-advisory

## Affected
- npm: `mathjs` — affected >=0 <7.5.1

## Details
The package mathjs before 7.5.1 are vulnerable to Prototype Pollution via the deepExtend function that runs upon configuration updates.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7743
- https://github.com/josdejong/mathjs/commit/ecb80514e80bce4e6ec7e71db8ff79954f07c57e
- https://github.com/josdejong/mathjs/blob/develop/HISTORY.md#2020-10-10-version-751
- https://github.com/josdejong/mathjs/blob/develop/src/utils/object.js%23L82
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARS-1017113
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSBOWER-1017112
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-1017111
- https://snyk.io/vuln/SNYK-JS-MATHJS-1016401
- https://www.npmjs.com/package/mathjs
