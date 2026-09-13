# [H] phpMyFAQ before 4.1.7 SQL Injection via Glossary

## Summary
Severity: High
Advisory: CVE-2026-76205
Aliases: GHSA-79h3-6hxj-g98h
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-19
Source: https://osv.dev/vulnerability/CVE-2026-76205
Type: osv

## Details
phpMyFAQ before 4.1.7 contains a SQL injection vulnerability in the glossary create and update endpoints caused by truncating an escaped string before embedding it in a SQL literal. Authenticated users with glossary add or edit permissions can craft a payload with a dangling backslash to escape the closing quote and inject arbitrary SQL commands to read sensitive database information.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/76xxx/CVE-2026-76205.json
- https://github.com/thorsten/phpMyFAQ/security/advisories/GHSA-79h3-6hxj-g98h
- https://nvd.nist.gov/vuln/detail/CVE-2026-76205
- https://www.vulncheck.com/advisories/phpmyfaq-before-sql-injection-via-glossary
