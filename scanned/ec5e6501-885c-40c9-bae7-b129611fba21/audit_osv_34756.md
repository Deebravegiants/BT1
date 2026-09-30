# [H] GLPI incorrectly authorizes access to documents

## Summary
Severity: High
Advisory: CVE-2025-64516
Aliases: GHSA-487h-7mxm-7r46
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-01-15
Source: https://osv.dev/vulnerability/CVE-2025-64516
Type: osv

## Details
GLPI is a free asset and IT management software package. Prior to 10.0.21 and 11.0.3, an unauthorized user can access GLPI documents attached to any item (ticket, asset, ...). If the public FAQ is enabled, this unauthorized access can be performed by an anonymous user. This vulnerability is fixed in 10.0.21 and 11.0.3.

## References
- https://github.com/glpi-project/glpi/releases/tag/10.0.21
- https://github.com/glpi-project/glpi/releases/tag/11.0.3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/64xxx/CVE-2025-64516.json
- https://github.com/glpi-project/glpi/security/advisories/GHSA-487h-7mxm-7r46
- https://nvd.nist.gov/vuln/detail/CVE-2025-64516
- https://github.com/glpi-project/glpi/commit/51412a89d3174cfe22967b051d527febdbceab3c
- https://github.com/glpi-project/glpi/commit/ee7ee28e0645198311c0a9e0c4e4b712b8788e27
