# [C] WeGIA has a SQL Injection endpoint 'adicionar_especie.php' parameter 'especie'

## Summary
Severity: Critical
Advisory: CVE-2025-23218
Aliases: GHSA-xhv4-88gx-hvgh
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2025-01-20
Source: https://osv.dev/vulnerability/CVE-2025-23218
Type: osv

## Details
WeGIA is an open source web manager with a focus on the Portuguese language and charitable institutions. A SQL Injection vulnerability was identified in the WeGIA application, specifically in the adicionar_especie.php endpoint. This vulnerability allows attackers to execute arbitrary SQL commands in the database, allowing unauthorized access to sensitive information. During the exploit, it was possible to perform a complete dump of the application's database, highlighting the severity of the flaw. This vulnerability is fixed in 3.2.10.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/23xxx/CVE-2025-23218.json
- https://github.com/LabRedesCefetRJ/WeGIA/security/advisories/GHSA-xhv4-88gx-hvgh
- https://nvd.nist.gov/vuln/detail/CVE-2025-23218
- https://github.com/LabRedesCefetRJ/WeGIA/commit/7465f785651c0cff65059bba96b015ab54235de4
