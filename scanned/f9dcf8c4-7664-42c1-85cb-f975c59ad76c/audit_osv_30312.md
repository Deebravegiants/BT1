# [H] GLPI vulnerable to unauthenticated session hijacking

## Summary
Severity: High
Advisory: CVE-2024-50339
Aliases: GHSA-v977-g4r9-6r72
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2024-12-11
Source: https://osv.dev/vulnerability/CVE-2024-50339
Type: osv

## Details
GLPI is a free asset and IT management software package. Starting in version 9.5.0 and prior to version 10.0.17, an unauthenticated user can retrieve all the sessions IDs and use them to steal any valid session. Version 10.0.17 contains a patch for this issue.

## References
- https://github.com/glpi-project/glpi/releases/tag/10.0.17
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50339.json
- https://github.com/glpi-project/glpi/security/advisories/GHSA-v977-g4r9-6r72
- https://nvd.nist.gov/vuln/detail/CVE-2024-50339
