# [C] Ghidra 11.0 < 12.1 - SQL Injection in PostgreSQL Password Change via Unescaped Username

## Summary
Severity: Critical
Advisory: CVE-2026-49498
Aliases: GHSA-vv7r-2rhf-5h7g
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-10
Source: https://osv.dev/vulnerability/CVE-2026-49498
Type: osv

## Details
Ghidra 11.0 before 12.1 contains a SQL injection vulnerability in the changePassword() method of PostgresFunctionDatabase that fails to escape double quotes in usernames interpolated into ALTER ROLE statements. Authenticated attackers can inject SQL commands via crafted username parameters in PasswordChange network messages to escalate to PostgreSQL superuser privileges and gain full database control.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/49xxx/CVE-2026-49498.json
- https://github.com/NationalSecurityAgency/ghidra/security/advisories/GHSA-vv7r-2rhf-5h7g
- https://nvd.nist.gov/vuln/detail/CVE-2026-49498
- https://www.vulncheck.com/advisories/ghidra-sql-injection-in-postgresql-password-change-via-unescaped-username
- https://github.com/nationalsecurityagency/ghidra
