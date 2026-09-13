# [H] GLPI vulnerable to authenticated insecure account deletion

## Summary
Severity: High
Advisory: CVE-2024-48912
Aliases: GHSA-vjmw-j32j-ph4f
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2024-12-11
Source: https://osv.dev/vulnerability/CVE-2024-48912
Type: osv

## Details
GLPI is a free asset and IT management software package. Starting in version 10.0.0 and prior to version 10.0.17, an authenticated user can use an application endpoint to delete any user account. Version 10.0.17 contains a patch for this issue.

## References
- https://github.com/glpi-project/glpi/releases/tag/10.0.17
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/48xxx/CVE-2024-48912.json
- https://github.com/glpi-project/glpi/security/advisories/GHSA-vjmw-j32j-ph4f
- https://nvd.nist.gov/vuln/detail/CVE-2024-48912
