# [H] Fields GLPI plugin has an Authenticated SQL Injection

## Summary
Severity: High
Advisory: CVE-2024-45600
Aliases: GHSA-wwxw-64g6-2992
CVSS: 7.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2024-12-26
Source: https://osv.dev/vulnerability/CVE-2024-45600
Type: osv

## Details
Fields is a GLPI plugin that allows users to add custom fields on GLPI items forms. Prior to 1.21.13, an authenticated user can perform a SQL injection when the plugin is active. The vulnerability is fixed in 1.21.13.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/45xxx/CVE-2024-45600.json
- https://github.com/pluginsGLPI/fields/security/advisories/GHSA-wwxw-64g6-2992
- https://nvd.nist.gov/vuln/detail/CVE-2024-45600
- https://github.com/pluginsGLPI/fields/commit/eb927b0f084ee4ef6c87ab2eb7a15e99369e74ae#diff-a7024a397fba9a026157683da73cc675ec6b73bd900374b3836bcdc76ec7bd5cR1166
