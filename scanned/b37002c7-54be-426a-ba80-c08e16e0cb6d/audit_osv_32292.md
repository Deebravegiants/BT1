# [H] GLPI Inventory plugin has Improper Access Control Vulnerability

## Summary
Severity: High
Advisory: CVE-2025-27147
Aliases: GHSA-h6x9-jm98-cw7c
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:L/A:L)
Published: 2025-03-25
Source: https://osv.dev/vulnerability/CVE-2025-27147
Type: osv

## Details
The GLPI Inventory Plugin handles various types of tasks for GLPI agents, including network discovery and inventory (SNMP), software deployment, VMWare ESX host remote inventory, and data collection (files, Windows registry, WMI). Versions prior to 1.5.0 have an improper access control vulnerability. Version 1.5.0 fixes the vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/27xxx/CVE-2025-27147.json
- https://github.com/glpi-project/glpi-inventory-plugin/security/advisories/GHSA-h6x9-jm98-cw7c
- https://nvd.nist.gov/vuln/detail/CVE-2025-27147
- https://github.com/glpi-project/glpi-inventory-plugin/commit/aaeb26d98d07019375c25b56e60fffc195553545
