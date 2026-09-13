# [C] Unauthenticated SQL Injection on get_socios.php endpoint

## Summary
Severity: Critical
Advisory: CVE-2025-46828
Aliases: GHSA-5qw5-q55h-6qg7
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2025-05-07
Source: https://osv.dev/vulnerability/CVE-2025-46828
Type: osv

## Details
WeGIA is a web manager for charitable institutions.  An unauthenticated SQL Injection vulnerability was identified in versions up to and including 3.3.0 in the endpoint `/html/socio/sistema/get_socios.php`, specifically in the query parameter. This issue allows attackers to inject and execute arbitrary SQL statements against the application's underlying database. As a result, it may lead to data exfiltration, authentication bypass, or complete database compromise. Version 3.3.1 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/46xxx/CVE-2025-46828.json
- https://github.com/LabRedesCefetRJ/WeGIA/security/advisories/GHSA-5qw5-q55h-6qg7
- https://nvd.nist.gov/vuln/detail/CVE-2025-46828
- https://github.com/LabRedesCefetRJ/WeGIA/commit/214dab59509bd3637f94adf381298c12da4ff80f
