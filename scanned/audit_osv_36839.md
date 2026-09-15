# [H] GLPI Inventory Plugin has SQL Injection on dropdown_calendar Report

## Summary
Severity: High
Advisory: CVE-2026-26001
Aliases: GHSA-gp4r-m42c-wvgx
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N)
Published: 2026-03-17
Source: https://osv.dev/vulnerability/CVE-2026-26001
Type: osv

## Details
The GLPI Inventory Plugin handles network discovery, inventory, software deployment, and data collection for GLPI agents. Prior to 1.6.6, non sanitized user input can lend to an SQL injection from reports, with adequate rights. This vulnerability is fixed in 1.6.6.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/26xxx/CVE-2026-26001.json
- https://github.com/glpi-project/glpi-inventory-plugin/security/advisories/GHSA-gp4r-m42c-wvgx
- https://nvd.nist.gov/vuln/detail/CVE-2026-26001
