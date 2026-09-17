# [C] GLPI vulnerable to SQL injection through dynamic reports

## Summary
Severity: Critical
Advisory: CVE-2023-28838
Aliases: GHSA-2c7r-gf38-358f
CVSS: 9.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N)
Published: 2023-04-05
Source: https://osv.dev/vulnerability/CVE-2023-28838
Type: osv

## Details
GLPI is a free asset and IT management software package. Starting in version 0.50 and prior to versions 9.5.13 and 10.0.7, a SQL Injection vulnerability allow users with access rights to statistics or reports to extract all data from database and, in some cases, write a webshell on the server. Versions 9.5.13 and 10.0.7 contain a patch for this issue. As a workaround, remove `Assistance > Statistics` and `Tools > Reports` read rights from every user.

## References
- https://github.com/glpi-project/glpi/releases/tag/10.0.7
- https://github.com/glpi-project/glpi/releases/tag/9.5.13
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/28xxx/CVE-2023-28838.json
- https://github.com/glpi-project/glpi/security/advisories/GHSA-2c7r-gf38-358f
- https://nvd.nist.gov/vuln/detail/CVE-2023-28838
