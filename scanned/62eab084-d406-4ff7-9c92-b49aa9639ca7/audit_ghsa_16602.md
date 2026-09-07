# [M] Thelia BackOffice default template vulnerable to Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-pp7v-wxx9-hm6r
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-05-30
Source: https://github.com/advisories/GHSA-pp7v-wxx9-hm6r
Type: github-advisory

## Affected
- Packagist: `thelia/backoffice-default-template` — affected >=2.1.0 <2.1.2

## Details
The BackOffice of Thelia (`error.html` template) has a cross-site scripting vulnerability in version 2.1.0 and 2.1.1 but not version 2.0.X. Version 2.1.2 contains a patch for the issue.

## References
- https://github.com/thelia-templates/back/commit/592612899057addc2613ccddf172024588277d2d
- https://github.com/FriendsOfPHP/security-advisories/blob/master/thelia/backoffice-default-template/2015-02-24-1.yaml
- https://github.com/thelia-templates/back
- https://thelia.net/version-2-1-2-with-security-fix
- https://web.archive.org/web/20160406004324/http://thelia.net/version-2-1-2-with-security-fix
