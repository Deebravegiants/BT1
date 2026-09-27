# [H] SQLBot: RCE via SQL Injection in Excel Upload Endpoint

## Summary
Severity: High
Advisory: CVE-2026-32950
Aliases: GHSA-7hww-8rj5-7rmm
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-03-20
Source: https://osv.dev/vulnerability/CVE-2026-32950
Type: osv

## Details
SQLBot is an intelligent data query system based on a large language model and RAG. Versions prior to 1.7.0 contain a critical SQL Injection vulnerability in the /api/v1/datasource/uploadExcel endpoint that enables Remote Code Execution (RCE), allowing any authenticated user (even the lowest-privileged) to fully compromise the backend server. The root cause is twofold: Excel Sheet names are concatenated directly into PostgreSQL table names without sanitization (datasource.py#L351), and those table names are embedded into COPY SQL statements via f-strings instead of parameterized queries (datasource.py#L385-L388). An attacker can bypass the 31-character Sheet name limit using a two-stage technique—first uploading a normal file whose data rows contain shell commands, then uploading an XML-tampered file whose Sheet name injects a TO PROGRAM 'sh' clause into the SQL. Confirmed impacts include arbitrary command execution as the postgres user (uid=999), sensitive file exfiltration (e.g., /etc/passwd, /etc/shadow), and complete PostgreSQL database takeover. This issue has been fixed in version 1.7.0.

## References
- https://github.com/dataease/SQLBot/releases/tag/v1.7.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/32xxx/CVE-2026-32950.json
- https://github.com/dataease/SQLBot/security/advisories/GHSA-7hww-8rj5-7rmm
- https://nvd.nist.gov/vuln/detail/CVE-2026-32950
- https://github.com/dataease/SQLBot/commit/39f2203cec4bb4b0aa541710733fe7608e3d3c48
