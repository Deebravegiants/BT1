# [M] Silverstripe: XSS in breadcrumbs in page list view

## Summary
Severity: Medium
Advisory: GHSA-w3cp-g2pf-65wh
CVE: CVE-2026-54717
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-08-06
Source: https://github.com/advisories/GHSA-w3cp-g2pf-65wh
Type: github-advisory

## Affected
- Packagist: `silverstripe/cms` — affected >=0 <6.2.1

## Details
### Impact
Page breadcrumbs in the CMS are vulnerable to XSS when viewed using the page list view

### Reporter
Fase Rais Baradika

## References
- https://github.com/silverstripe/silverstripe-cms/security/advisories/GHSA-w3cp-g2pf-65wh
- https://github.com/silverstripe/silverstripe-cms/pull/3175
- https://github.com/silverstripe/silverstripe-cms/commit/62f9912baa18c80304f3fa8b6eca71bb5dc2d21e
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/cms/CVE-2026-54717.yaml
- https://github.com/silverstripe/silverstripe-cms
- https://github.com/silverstripe/silverstripe-cms/releases/tag/6.2.1
- https://www.silverstripe.org/download/security-releases/cve-2026-54717
