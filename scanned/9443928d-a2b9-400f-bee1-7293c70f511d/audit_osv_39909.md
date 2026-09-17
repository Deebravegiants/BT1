# [M] Open ISES Tickets < 3.44.2 SQL Injection via portal/ajax/list_requests.php sort and dir Parameters

## Summary
Severity: Medium
Advisory: CVE-2026-48234
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N)
Published: 2026-05-21
Source: https://osv.dev/vulnerability/CVE-2026-48234
Type: osv

## Details
Open ISES Tickets before 3.44.2 contains a SQL injection vulnerability in portal/ajax/list_requests.php where the sort and dir GET parameters are concatenated into the ORDER BY clause of a SELECT statement without sanitization. Authenticated attackers can craft requests that alter query semantics to read, modify, or destroy database contents.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48234.json
- https://github.com/openises/tickets/releases/tag/v3.44.2
- https://nvd.nist.gov/vuln/detail/CVE-2026-48234
- https://www.vulncheck.com/advisories/open-ises-tickets-sql-injection-via-portal-ajax-list-requests-php-sort-and-dir-parameters
- https://github.com/openises/tickets/commit/ecfeb406a016766cae81c749e14b5145a9f2dbff
