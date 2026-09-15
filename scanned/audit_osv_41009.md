# [C] Adminer before 5.4.3 Remote Code Execution via MSSQL PDO DSN Injection

## Summary
Severity: Critical
Advisory: CVE-2026-56705
Aliases: GHSA-r4x9-5m63-3vxw
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-56705
Type: osv

## Details
Adminer before 5.4.3 fails to sanitize the server field before constructing a PDO DSN string, allowing unauthenticated attackers to inject ODBC parameters via semicolons. Attackers can inject TraceFile and TraceOn parameters to write PHP code to the web root, achieving remote code execution when the trace file is accessed.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56705.json
- https://github.com/vrana/adminer/security/advisories/GHSA-r4x9-5m63-3vxw
- https://nvd.nist.gov/vuln/detail/CVE-2026-56705
- https://www.vulncheck.com/advisories/adminer-before-remote-code-execution-via-mssql-pdo-dsn-injection
