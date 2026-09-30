# [H] CVE-2020-11004

## Summary
Severity: High
Advisory: CVE-2020-11004
Aliases: GHSA-qh57-rcff-gx54
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-04-24
Source: https://osv.dev/vulnerability/CVE-2020-11004
Type: osv

## Details
SQL Injection was discovered in Admidio before version 3.3.13. The main cookie parameter is concatenated into a SQL query without any input validation/sanitization, thus an attacker without logging in, can send a GET request with arbitrary SQL queries appended to the cookie parameter and execute SQL queries. The vulnerability impacts the confidentiality of the system. This has been patched in version 3.3.13.

## References
- https://github.com/Admidio/admidio/issues/908
- https://github.com/Admidio/admidio/security/advisories/GHSA-qh57-rcff-gx54
- https://github.com/Admidio/admidio/commit/ea5d6f114b151ed11ec0ad7cb47bd729e77a874a
