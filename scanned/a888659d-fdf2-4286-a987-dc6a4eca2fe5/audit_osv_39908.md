# [M] Open ISES Tickets < 3.44.2 SQL Injection via ajax/fullsit_incidents.php offset Parameter

## Summary
Severity: Medium
Advisory: CVE-2026-48232
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N)
Published: 2026-05-21
Source: https://osv.dev/vulnerability/CVE-2026-48232
Type: osv

## Details
Open ISES Tickets before 3.44.2 contains a SQL injection vulnerability in ajax/fullsit_incidents.php where the offset GET parameter is concatenated into the LIMIT clause of a SELECT statement without sanitization. Authenticated attackers can craft requests that alter query semantics to read, modify, or destroy database contents.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48232.json
- https://github.com/openises/tickets/releases/tag/v3.44.2
- https://nvd.nist.gov/vuln/detail/CVE-2026-48232
- https://www.vulncheck.com/advisories/open-ises-tickets-sql-injection-via-ajax-fullsit-incidents-php-offset-parameter
- https://github.com/openises/tickets/commit/ecfeb406a016766cae81c749e14b5145a9f2dbff
