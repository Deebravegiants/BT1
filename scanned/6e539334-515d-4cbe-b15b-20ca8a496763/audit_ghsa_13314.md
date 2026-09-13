# [H] Cockpit CMS vulnerable to incorrect access control

## Summary
Severity: High
Advisory: GHSA-9r25-4j77-9wc7
CVE: CVE-2023-37649
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-07-20
Source: https://github.com/advisories/GHSA-9r25-4j77-9wc7
Type: github-advisory

## Affected
- Packagist: `cockpit-hq/cockpit` — affected >=0 <2.6.0

## Details
Incorrect access control in the component `/models/Content` of Cockpit CMS v2.5.2 allows unauthorized attackers to access sensitive data.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-37649
- https://github.com/Cockpit-HQ/Cockpit
- https://github.com/Cockpit-HQ/Cockpit/releases/tag/2.6.0
- https://www.ghostccamm.com/blog/multi_cockpit_vulns
