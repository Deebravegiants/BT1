# [M] Open ISES Tickets < 3.44.2 SQL Injection via message.php frm_ticket_id and frm_resp_id Parameters

## Summary
Severity: Medium
Advisory: CVE-2026-48237
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N)
Published: 2026-05-21
Source: https://osv.dev/vulnerability/CVE-2026-48237
Type: osv

## Details
Open ISES Tickets before 3.44.2 contains a SQL injection vulnerability in message.php where the frm_ticket_id and frm_resp_id POST parameters are concatenated into WHERE clauses of SELECT/UPDATE statements without sanitization. Authenticated attackers can craft requests that alter query semantics to read, modify, or destroy database contents.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48237.json
- https://github.com/openises/tickets/releases/tag/v3.44.2
- https://nvd.nist.gov/vuln/detail/CVE-2026-48237
- https://www.vulncheck.com/advisories/open-ises-tickets-sql-injection-via-message-php-frm-ticket-id-and-frm-resp-id-parameters
- https://github.com/openises/tickets/commit/ecfeb406a016766cae81c749e14b5145a9f2dbff
