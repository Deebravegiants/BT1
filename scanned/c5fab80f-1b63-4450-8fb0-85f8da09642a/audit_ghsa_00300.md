# [M] Regular Expression Denial Of Service in uri-js

## Summary
Severity: Medium
Advisory: GHSA-333w-rxj3-f55r
CVE: CVE-2017-16021
CWE: CWE-1333, CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2018-07-24
Source: https://github.com/advisories/GHSA-333w-rxj3-f55r
Type: github-advisory

## Affected
- npm: `uri-js` — affected >=0 <3.0.0

## Details
Affected versions of `uri-js` is susceptible to a regular expression denial of service vulnerability when user input is sent to the `.parse()` method.



## Recommendation

Update to v3.0.0 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16021
- https://github.com/garycourt/uri-js/issues/12
- https://github.com/advisories/GHSA-333w-rxj3-f55r
- https://nodesecurity.io/advisories/100
- https://www.npmjs.com/advisories/100
