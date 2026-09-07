# [M] Craft CMS Audit Plugin Cross Site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-v89q-c273-3p42
CVE: CVE-2023-36259
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-01-30
Source: https://github.com/advisories/GHSA-v89q-c273-3p42
Type: github-advisory

## Affected
- Packagist: `superbig/craft-audit` — affected >=0 <3.0.2

## Details
Cross Site Scripting (XSS) vulnerability in Craft CMS Audit Plugin before version 3.0.2 allows attackers to execute arbitrary code during user creation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-36259
- https://github.com/sjelfull/craft-audit/pull/73
- https://github.com/sjelfull/craft-audit/commit/c2888aa48457f24696ac0a2ba4f54f39e5c672ed
- https://github.com/sjelfull/craft-audit
- https://www.linkedin.com/pulse/threat-briefing-craftcms-amrcybersecurity-emi0e/?trackingId=E75GttWvQp6gfvPiJDDUBA%3D%3D
