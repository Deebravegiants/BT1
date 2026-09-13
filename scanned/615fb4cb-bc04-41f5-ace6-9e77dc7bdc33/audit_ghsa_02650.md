# [M] Path Traversal in serve-here.js

## Summary
Severity: Medium
Advisory: GHSA-4448-rc82-fcr7
CVE: CVE-2019-5444
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2021-09-22
Source: https://github.com/advisories/GHSA-4448-rc82-fcr7
Type: github-advisory

## Affected
- npm: `serve-here.js` — affected >=0 <1.2.0

## Details
Versions of serve-here.js prior to 1.2.0 are vulnerable to path traversal. The package fails to sanitize URLs, allowing attackers to access server files outside of the served folder using relative paths.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-5444
- https://hackerone.com/reports/569966
- https://github.com/ChristoPy/serve-here.js
- https://www.npmjs.com/advisories/1019
