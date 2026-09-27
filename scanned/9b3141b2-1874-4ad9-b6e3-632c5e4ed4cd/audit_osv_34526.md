# [C] WeGIA: SQL Injection (Blind Time-Based) Vulnerability in API `descricao` Parameter

## Summary
Severity: Critical
Advisory: CVE-2025-61603
Aliases: GHSA-v8hm-pq8g-c7j4
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2025-10-02
Source: https://osv.dev/vulnerability/CVE-2025-61603
Type: osv

## Details
WeGIA is a Web manager for charitable institutions. Versions 3.4.12 and below include an SQL Injection vulnerability which was identified in the /controle/control.php endpoint, specifically in the descricao parameter. This vulnerability allows attackers to execute arbitrary SQL commands, compromising the confidentiality, integrity, and availability of the database. This issue is fixed in version 3.5.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/61xxx/CVE-2025-61603.json
- https://github.com/LabRedesCefetRJ/WeGIA/security/advisories/GHSA-v8hm-pq8g-c7j4
- https://nvd.nist.gov/vuln/detail/CVE-2025-61603
- https://github.com/LabRedesCefetRJ/WeGIA/commit/84958eed73741a544859eea297908db3b83b3833
