# [H] Path Traversal in crud-file-server

## Summary
Severity: High
Advisory: GHSA-vfp9-gwrh-wq9g
CVE: CVE-2018-3733
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2018-07-18
Source: https://github.com/advisories/GHSA-vfp9-gwrh-wq9g
Type: github-advisory

## Affected
- npm: `crud-file-server` — affected >=0 <0.9.0

## Details
Versions of `crud-file-server` prior to 0.9.0 are vulnerable to Path Traversal. The package fails to sanitize URLs, allowing attackers to access server files outside of the served folder using relative paths.


## Recommendation

Upgrade to version 0.9.0 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-3733
- https://github.com/omphalos/crud-file-server/commit/4fc3b404f718abb789f4ce4272c39c7a138c7a82
- https://hackerone.com/reports/310690
- https://github.com/advisories/GHSA-vfp9-gwrh-wq9g
- https://www.npmjs.com/advisories/1003
