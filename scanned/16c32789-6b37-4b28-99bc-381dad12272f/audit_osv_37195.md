# [M] Authenticated SuiteCRM Users Can Retrieve The Password Hash of Any User

## Summary
Severity: Medium
Advisory: CVE-2026-29108
Aliases: GHSA-xc8w-xc9v-45w5
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-03-19
Source: https://osv.dev/vulnerability/CVE-2026-29108
Type: osv

## Details
SuiteCRM is an open-source, enterprise-ready Customer Relationship Management (CRM) software application. Prior to versions 8.9.3, an authenticated API endpoint allows any user to retrieve detailed information about any other user, including their password hash, username, and MFA configuration. As any authenticated user can query this endpoint, it's possible to retrieve and potentially crack the passwords of administrative users. Version 8.9.3 patches the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/29xxx/CVE-2026-29108.json
- https://github.com/SuiteCRM/SuiteCRM-Core/security/advisories/GHSA-xc8w-xc9v-45w5
- https://nvd.nist.gov/vuln/detail/CVE-2026-29108
