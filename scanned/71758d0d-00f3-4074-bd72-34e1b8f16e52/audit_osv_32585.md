# [H] GLPI Inventory Plugin is Vulnerable to Unauthenticated SQL Injection

## Summary
Severity: High
Advisory: CVE-2025-32786
Aliases: GHSA-w2cp-r675-6xpq
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-11-04
Source: https://osv.dev/vulnerability/CVE-2025-32786
Type: osv

## Details
The GLPI Inventory Plugin handles network discovery, inventory, software deployment, and data collection for GLPI agents. Versions 1.5.0 and below are vulnerable to SQL Injection. This issue is fixed in version 1.5.1.

## References
- https://github.com/glpi-project/glpi-inventory-plugin/blob/1.5.1/CHANGELOG.md
- https://github.com/glpi-project/glpi-inventory-plugin/releases/tag/1.5.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/32xxx/CVE-2025-32786.json
- https://github.com/glpi-project/glpi-inventory-plugin/security/advisories/GHSA-w2cp-r675-6xpq
- https://nvd.nist.gov/vuln/detail/CVE-2025-32786
