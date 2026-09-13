# [M] WeGIA allows Time-Based Blind SQL Injection in the relatorio_geracao.php endpoint

## Summary
Severity: Medium
Advisory: CVE-2025-53527
Aliases: GHSA-43xw-c4g6-jgff
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N)
Published: 2025-07-07
Source: https://osv.dev/vulnerability/CVE-2025-53527
Type: osv

## Details
WeGIA is a web manager for charitable institutions. A Time-Based Blind SQL Injection vulnerability was discovered in the almox parameter of the /controle/relatorio_geracao.php endpoint. This issue allows attacker to inject arbitrary SQL queries, potentially leading to unauthorized data access or further exploitation depending on database configuration. This vulnerability is fixed in 3.4.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/53xxx/CVE-2025-53527.json
- https://github.com/LabRedesCefetRJ/WeGIA/security/advisories/GHSA-43xw-c4g6-jgff
- https://nvd.nist.gov/vuln/detail/CVE-2025-53527
- https://github.com/LabRedesCefetRJ/WeGIA/commit/9de9a741d1d26ae76b2215a32660817d9bd452aa
