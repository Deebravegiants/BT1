# [H] Path Traversal in buttle

## Summary
Severity: High
Advisory: GHSA-m8cr-q935-8j67
CVE: CVE-2018-3766
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2018-09-18
Source: https://github.com/advisories/GHSA-m8cr-q935-8j67
Type: github-advisory

## Affected
- npm: `buttle` — affected >=0

## Details
All versions of `buttle` are vulnerable to Path Traversal.  Due to insufficient input sanitization, attackers can access server files by using relative paths when fetching files. 


## Recommendation

No fix is currently available. Consider using an alternative module until a fix is made available.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-3766
- https://hackerone.com/reports/358112
- https://github.com/advisories/GHSA-m8cr-q935-8j67
- https://www.npmjs.com/advisories/990
