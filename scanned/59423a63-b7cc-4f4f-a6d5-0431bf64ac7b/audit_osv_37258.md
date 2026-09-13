# [H] CVE-2026-30461

## Summary
Severity: High
Advisory: CVE-2026-30461
CVSS: 8.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:L)
Published: 2026-04-15
Source: https://osv.dev/vulnerability/CVE-2026-30461
Type: osv

## Details
Daylight Studio FuelCMS v1.5.2 was discovered to contain an authenticated remote code execution (RCE) vulnerability via the /controllers/Installer.php and the function add_git_submodule.

## References
- https://github.com/daylightstudio/FUEL-CMS/blob/master/fuel/modules/fuel/controllers/Installer.php
- https://pentest-tools.com/PTT-2025-028-Authenticated-RCE-via-Git-Submodules.pdf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/30xxx/CVE-2026-30461.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-30461
