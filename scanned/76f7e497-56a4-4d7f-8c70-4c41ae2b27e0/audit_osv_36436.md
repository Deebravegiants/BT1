# [C] Fields GLPI plugin vulnerable to RCE in dropdown generation

## Summary
Severity: Critical
Advisory: CVE-2026-23489
Aliases: GHSA-rj7q-mmx9-fhq7
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-03-16
Source: https://osv.dev/vulnerability/CVE-2026-23489
Type: osv

## Details
Fields is a GLPI plugin that allows users to add custom fields on GLPI items forms. Prior to version 1.23.3, it is possible to execute arbitrary PHP code from users that are allowed to create dropdowns. This issue has been patched in version 1.23.3.

## References
- https://github.com/pluginsGLPI/fields/releases/tag/1.23.3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23489.json
- https://github.com/pluginsGLPI/fields/security/advisories/GHSA-rj7q-mmx9-fhq7
- https://nvd.nist.gov/vuln/detail/CVE-2026-23489
