# [H] Path Traversal in resolve-path

## Summary
Severity: High
Advisory: GHSA-62g9-6hw5-rwfp
CVE: CVE-2018-3732
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2018-07-18
Source: https://github.com/advisories/GHSA-62g9-6hw5-rwfp
Type: github-advisory

## Affected
- npm: `resolve-path` — affected >=0 <1.4.0

## Details
Versions of `resolve-path` before 1.4.0 are vulnerable to path traversal. `resolve-path` relative path resolving suffers from a lack of file path sanitization for windows based paths.


## Recommendation

Update to version 1.4.0 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-3732
- https://github.com/pillarjs/resolve-path/commit/fe5b8052cafd35fcdafe9210e100e9050b37d2a0
- https://hackerone.com/reports/315760
- https://github.com/advisories/GHSA-62g9-6hw5-rwfp
- https://www.npmjs.com/advisories/573
