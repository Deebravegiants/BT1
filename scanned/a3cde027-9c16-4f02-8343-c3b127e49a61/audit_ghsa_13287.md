# [H] Cockpit CMS Cross-Site Request Forgery vulnerability

## Summary
Severity: High
Advisory: GHSA-45g2-r339-pjwf
CVE: CVE-2023-37650
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-07-20
Source: https://github.com/advisories/GHSA-45g2-r339-pjwf
Type: github-advisory

## Affected
- Packagist: `cockpit-hq/cockpit` — affected >=0 <2.6.0

## Details
A Cross-Site Request Forgery (CSRF) in the Admin portal of Cockpit CMS v2.5.2 allows attackers to execute arbitrary Administrator commands.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-37650
- https://github.com/Cockpit-HQ/Cockpit
- https://github.com/Cockpit-HQ/Cockpit/releases/tag/2.6.0
- https://www.ghostccamm.com/blog/multi_cockpit_vulns
