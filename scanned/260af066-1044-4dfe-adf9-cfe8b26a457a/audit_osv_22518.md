# [M] SQL Injection via package deployment tasks in glpi-inventory-plugin

## Summary
Severity: Medium
Advisory: CVE-2022-31082
Aliases: GHSA-q6m7-h6rj-5wmw
CVSS: 5.8 (CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:C/C:H/I:N/A:N)
Published: 2022-06-27
Source: https://osv.dev/vulnerability/CVE-2022-31082
Type: osv

## Details
GLPI is a Free Asset and IT Management Software package, Data center management, ITIL Service Desk, licenses tracking and software auditing. glpi-inventory-plugin is a plugin for GLPI to handle inventory management. In affected versions a SQL injection can be made using package deployment tasks. This issue has been resolved in version 1.0.2. Users are advised to upgrade. Users unable to upgrade should delete the `front/deploypackage.public.php` file if they are not using the `deploy tasks` feature.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/31xxx/CVE-2022-31082.json
- https://github.com/glpi-project/glpi-inventory-plugin/security/advisories/GHSA-q6m7-h6rj-5wmw
- https://nvd.nist.gov/vuln/detail/CVE-2022-31082
- https://github.com/glpi-project/glpi-inventory-plugin/commit/0b805ca6fb2a0f9bde4af29fca4f703fdfbd8f66
