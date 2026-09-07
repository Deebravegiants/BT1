# [M] phppgadmin contains an incorrect access control vulnerability

## Summary
Severity: Medium
Advisory: GHSA-r63p-v37q-g74c
CVE: CVE-2025-60799
CWE: CWE-284
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-11-20
Source: https://github.com/advisories/GHSA-r63p-v37q-g74c
Type: github-advisory

## Affected
- Packagist: `phppgadmin/phppgadmin` — affected >=0

## Details
phpPgAdmin 7.13.0 and earlier contains an incorrect access control vulnerability in sql.php at lines 68-76. The application allows unauthorized manipulation of session variables by accepting user-controlled parameters ('subject', 'server', 'database', 'queryid') without proper validation or access control checks. Attackers can exploit this to store arbitrary SQL queries in $_SESSION['sqlquery'] by manipulating these parameters, potentially leading to session poisoning, stored cross-site scripting, or unauthorized access to sensitive session data.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-60799
- https://github.com/phppgadmin/phppgadmin
- https://github.com/phppgadmin/phppgadmin/blob/master/sql.php#L68-L76
- https://github.com/pr0wl1ng/security-advisories/blob/main/CVE-2025-60799.md
