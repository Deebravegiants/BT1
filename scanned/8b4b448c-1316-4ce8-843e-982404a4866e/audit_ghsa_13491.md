# [M] Evolution CMS Cross-site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-432f-967f-vxg4
CVE: CVE-2023-43340
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-10-20
Source: https://github.com/advisories/GHSA-432f-967f-vxg4
Type: github-advisory

## Affected
- Packagist: `evolutioncms/evolution` — affected >=0

## Details
Cross-site scripting (XSS) vulnerability in evolution v.3.2.3 allows a local attacker to execute arbitrary code via a crafted payload injected into the cmsadmin, cmsadminemail, cmspassword and cmspasswordconfim parameters

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-43340
- https://github.com/evolution-cms/evolution
- https://github.com/sromanhu/-CVE-2023-43340-Evolution-Reflected-XSS---Installation-Admin-Options
- https://github.com/sromanhu/Evolution-Reflected-XSS---Installation-Admin-Options
