# [M] Path Traversal in statichttpserver

## Summary
Severity: Medium
Advisory: GHSA-2j5x-56p6-hj6x
CVE: CVE-2019-5480
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2019-09-04
Source: https://github.com/advisories/GHSA-2j5x-56p6-hj6x
Type: github-advisory

## Affected
- npm: `statichttpserver` — affected >=0

## Details
All versions of `statichttpserver` are vulnerable to Path Traversal. The package fails to sanitize URLs, allowing attackers to access server files outside of the served folder using relative paths.


## Recommendation

No fix is currently available. Consider using an alternative package until a fix is made available.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-5480
- https://hackerone.com/reports/570035
- https://www.npmjs.com/advisories/1143
