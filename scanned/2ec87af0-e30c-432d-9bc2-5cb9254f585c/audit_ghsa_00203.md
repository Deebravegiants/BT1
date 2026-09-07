# [M] Cross-site Scripting (XSS) - Stored in crud-file-server

## Summary
Severity: Medium
Advisory: GHSA-h24f-9mm4-w336
CVE: CVE-2018-3726
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2018-07-18
Source: https://github.com/advisories/GHSA-h24f-9mm4-w336
Type: github-advisory

## Affected
- npm: `crud-file-server` — affected >=0 <0.8.0

## Details
Versions of `crud-file-server` before 0.8.0 are vulnerable to stored cross-site scripting (XSS). This is due to insufficient santiziation of filenames when directory index is served by `crud-file-server`.


## Recommendation

Update to version 0.8.0 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-3726
- https://github.com/omphalos/crud-file-server/commit/4155bfe068bf211b49a0b3ffd06e78cbaf1b40fa
- https://hackerone.com/reports/311101
- https://github.com/advisories/GHSA-h24f-9mm4-w336
- https://www.npmjs.com/advisories/570
