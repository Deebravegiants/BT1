# [H] Path Traversal in 626

## Summary
Severity: High
Advisory: GHSA-r4r9-mgjc-g6q3
CVE: CVE-2018-3727
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2020-09-01
Source: https://github.com/advisories/GHSA-r4r9-mgjc-g6q3
Type: github-advisory

## Affected
- npm: `626` — affected >=0.0.0

## Details
All versions of `626` are vulnerable to path traversal. This enables a remote attacker to read arbitrary files from the remote server using this module.


## Recommendation

No fix is currently available for this vulnerability.
It is our recommendation to not install or use this module at this time.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-3727
- https://hackerone.com/reports/311216
