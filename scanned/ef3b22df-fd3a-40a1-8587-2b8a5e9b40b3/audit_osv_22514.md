# [M] Sensitive Data Exposure on Refused Inventory Files in GLPI

## Summary
Severity: Medium
Advisory: CVE-2022-31068
Aliases: GHSA-g4hm-6vfr-q3wg
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2022-06-28
Source: https://osv.dev/vulnerability/CVE-2022-31068
Type: osv

## Details
GLPI is a Free Asset and IT Management Software package, Data center management, ITIL Service Desk, licenses tracking and software auditing. In affected versions all GLPI instances with the native inventory used may leak sensitive information. The feature to get refused file is not authenticated. This issue has been addressed in version 10.0.2 and all affected users are advised to upgrade.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/31xxx/CVE-2022-31068.json
- https://github.com/glpi-project/glpi/security/advisories/GHSA-g4hm-6vfr-q3wg
- https://nvd.nist.gov/vuln/detail/CVE-2022-31068
- https://github.com/glpi-project/glpi/commit/9953a644777e4167b06db9e14fc93b945a557be5
