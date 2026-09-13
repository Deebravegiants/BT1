# [H] Path Traversal in serve

## Summary
Severity: High
Advisory: GHSA-v588-qcp3-jv46
CVE: CVE-2019-5415
CWE: CWE-548
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2019-03-25
Source: https://github.com/advisories/GHSA-v588-qcp3-jv46
Type: github-advisory

## Affected
- npm: `serve` — affected >=0 <7.0.0

## Details
Versions of `serve` prior to 7.0.1 are vulnerable to Path Traversal. Explicitly ignored folders can be accessed through if the path contains a `/./`, which allows attackers to access hidden folders and files.


## Recommendation

Upgrade to version 7.0.1 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-5415
- https://hackerone.com/reports/330724
- https://github.com/advisories/GHSA-v588-qcp3-jv46
- https://www.npmjs.com/advisories/1010
