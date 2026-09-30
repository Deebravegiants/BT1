# [C] WeGIA vulnerable to SQL Injection (Blind Time-Based) in endpoint 'Profile_Atendido.php' parameter 'idatendido'

## Summary
Severity: Critical
Advisory: CVE-2025-54079
Aliases: GHSA-g4v3-j8w5-33v3
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2025-07-18
Source: https://osv.dev/vulnerability/CVE-2025-54079
Type: osv

## Details
WeGIA is an open source web manager with a focus on the Portuguese language and charitable institutions. A SQL Injection vulnerability was identified in versions prior to 3.4.6 in the endpoint `/html/atendido/Profile_Atendido.php`, in the `idatendido` parameter. This vulnerability allow an authorized attacker to execute arbitrary SQL queries, allowing access to sensitive information. Version 3.4.6 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/54xxx/CVE-2025-54079.json
- https://github.com/LabRedesCefetRJ/WeGIA/security/advisories/GHSA-g4v3-j8w5-33v3
- https://nvd.nist.gov/vuln/detail/CVE-2025-54079
