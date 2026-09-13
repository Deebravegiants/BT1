# [H] Path Traversal in stattic

## Summary
Severity: High
Advisory: GHSA-w4pv-w56c-mg4v
CVE: CVE-2018-3734
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2018-07-18
Source: https://github.com/advisories/GHSA-w4pv-w56c-mg4v
Type: github-advisory

## Affected
- npm: `stattic` — affected >=0 <0.3.0

## Details
Versions of `stattic` before 0.3.0 are vulnerable to path traversal allowing a remote attacker to read arbitrary files with any extension from the server that users `stattic`.


## Recommendation

Update to version 0.3.0 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-3734
- https://hackerone.com/reports/319003
- https://github.com/advisories/GHSA-w4pv-w56c-mg4v
- https://www.npmjs.com/advisories/591
