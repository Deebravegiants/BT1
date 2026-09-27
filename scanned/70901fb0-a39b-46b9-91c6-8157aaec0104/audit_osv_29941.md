# [H] GLPI vulnerable to account takeover without privilege escalation through the API

## Summary
Severity: High
Advisory: CVE-2024-47758
Aliases: GHSA-3r4x-6pmx-phwr
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2024-12-11
Source: https://osv.dev/vulnerability/CVE-2024-47758
Type: osv

## Details
GLPI is a free asset and IT management software package. Starting in version 9.3.0 and prior to version 10.0.17, an authenticated user can use the API to take control of any user that have the same or a lower level of privileges. Version 10.0.17 contains a patch for this issue.

## References
- https://github.com/glpi-project/glpi/releases/tag/10.0.17
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/47xxx/CVE-2024-47758.json
- https://github.com/glpi-project/glpi/security/advisories/GHSA-3r4x-6pmx-phwr
- https://nvd.nist.gov/vuln/detail/CVE-2024-47758
