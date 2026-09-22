# [C] GLPI vulnerable to account takeover via API

## Summary
Severity: Critical
Advisory: CVE-2024-47760
Aliases: GHSA-r3mx-fr5f-gwgp
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2024-12-11
Source: https://osv.dev/vulnerability/CVE-2024-47760
Type: osv

## Details
GLPI is a free asset and IT management software package. Starting in version 9.1.0 and prior to version 10.0.17, a technician with an access to the API can take control of an account with higher privileges. Version 10.0.17 contains a patch for this issue.

## References
- https://github.com/glpi-project/glpi/releases/tag/10.0.17
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/47xxx/CVE-2024-47760.json
- https://github.com/glpi-project/glpi/security/advisories/GHSA-r3mx-fr5f-gwgp
- https://nvd.nist.gov/vuln/detail/CVE-2024-47760
