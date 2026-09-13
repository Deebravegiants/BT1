# [M] WWBN AVideo SQL Injection via get.json.php APIName channels

## Summary
Severity: Medium
Advisory: CVE-2026-85155
Aliases: GHSA-pmmj-6425-gpgh
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-85155
Type: osv

## Details
WWBN AVideo contains a SQL injection vulnerability in the sort column parameter of the get.json.php endpoint with APIName=channels that allows unauthenticated attackers to order results by arbitrary database columns including users.password and users.recoverPass. Attackers can exploit this ordering oracle to infer password hash values and recovery tokens, and trigger SQL errors that disclose the full query statement and database schema.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85155.json
- https://github.com/WWBN/AVideo/security/advisories/GHSA-pmmj-6425-gpgh
- https://nvd.nist.gov/vuln/detail/CVE-2026-85155
- https://www.vulncheck.com/advisories/wwbn-avideo-sql-injection-via-get-json-php-apiname-channels
