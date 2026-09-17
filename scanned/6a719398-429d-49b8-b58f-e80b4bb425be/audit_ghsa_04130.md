# [H] Directory Traversal in serve

## Summary
Severity: High
Advisory: GHSA-xg75-3277-gvvj
CVE: CVE-2019-5417
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2019-03-25
Source: https://github.com/advisories/GHSA-xg75-3277-gvvj
Type: github-advisory

## Affected
- npm: `serve` — affected >=0 <7.1.3

## Details
Versions of `serve` before 7.1.3 are vulnerable to Directory Traversal. File paths are not sanitized leading to unauthorized access of system files.


## Recommendation

Upgrade to version 7.1.3 or later

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-5417
- https://hackerone.com/reports/358645
- https://github.com/advisories/GHSA-xg75-3277-gvvj
- https://www.npmjs.com/advisories/795
