# [H] Chartbrew: SQL injection in date-type variable handling (applyMysqlOrPostgresVariables)

## Summary
Severity: High
Advisory: CVE-2026-27005
Aliases: GHSA-w5rh-v333-qq6c
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N/E:P)
Published: 2026-03-06
Source: https://osv.dev/vulnerability/CVE-2026-27005
Type: osv

## Details
Chartbrew is an open-source web application that can connect directly to databases and APIs and use the data to create charts. Prior to version 4.8.3, an unauthenticated attacker can inject arbitrary SQL into queries executed against databases connected to Chartbrew (MySQL, PostgreSQL). This allows reading, modifying, or deleting data in those databases depending on the database user's privileges. This issue has been patched in version 4.8.3.

## References
- https://github.com/chartbrew/chartbrew/releases/tag/v4.8.3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27005.json
- https://github.com/chartbrew/chartbrew/security/advisories/GHSA-w5rh-v333-qq6c
- https://nvd.nist.gov/vuln/detail/CVE-2026-27005
