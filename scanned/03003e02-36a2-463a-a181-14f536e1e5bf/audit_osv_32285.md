# [C] WeGIA has SQL Injection endpoint at 'dao/pet/adicionar_tipo_exame.php' parameter 'tipo_exame'

## Summary
Severity: Critical
Advisory: CVE-2025-27133
Aliases: GHSA-xj79-w799-qjcp
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2025-02-24
Source: https://osv.dev/vulnerability/CVE-2025-27133
Type: osv

## Details
WeGIA is a Web manager for charitable institutions. A SQL Injection vulnerability was discovered in the WeGIA application prior to version 3.2.15 at the `adicionar_tipo_exame.php` endpoint. This vulnerability allows an authorized attacker to execute arbitrary SQL queries, allowing access to sensitive information. Version 3.2.15 contains a patch for the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/27xxx/CVE-2025-27133.json
- https://github.com/LabRedesCefetRJ/WeGIA/security/advisories/GHSA-xj79-w799-qjcp
- https://nvd.nist.gov/vuln/detail/CVE-2025-27133
- https://github.com/LabRedesCefetRJ/WeGIA/commit/619ead748e18e685459c6dc3c226e621b9ff5403
