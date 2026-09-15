# [C] Ghidra < 12.1 - SQL Injection via Unescaped Filter Values in BSim Search

## Summary
Severity: Critical
Advisory: CVE-2026-52758
Aliases: GHSA-8r4f-65cr-fwxm
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-10
Source: https://osv.dev/vulnerability/CVE-2026-52758
Type: osv

## Details
Ghidra before 12.1 contains a SQL injection vulnerability in BSim filter types that concatenate user-supplied values directly into SQL queries without escaping or parameterization. Remote attackers can inject arbitrary SQL via the BSim network query protocol to read, modify, or delete data in the PostgreSQL database.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/52xxx/CVE-2026-52758.json
- https://github.com/NationalSecurityAgency/ghidra/security/advisories/GHSA-8r4f-65cr-fwxm
- https://nvd.nist.gov/vuln/detail/CVE-2026-52758
- https://www.vulncheck.com/advisories/ghidra-sql-injection-via-unescaped-filter-values-in-bsim-search
- https://github.com/nationalsecurityagency/ghidra
