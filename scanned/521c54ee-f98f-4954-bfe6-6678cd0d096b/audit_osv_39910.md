# [M] Open ISES Tickets < 3.44.2 SQL Injection in incs/remotes.inc.php via External GPS Tracker Data

## Summary
Severity: Medium
Advisory: CVE-2026-48235
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N)
Published: 2026-05-21
Source: https://osv.dev/vulnerability/CVE-2026-48235
Type: osv

## Details
Open ISES Tickets before 3.44.2 contains a SQL injection vulnerability in incs/remotes.inc.php where latitude, longitude, callsign, mph, altitude, and timestamp values parsed from external GPS tracking service XML/JSON responses (InstaMapper and Google Latitude integration) are concatenated into UPDATE and INSERT statements without sanitization. An attacker able to compromise or impersonate the remote GPS tracker endpoint can inject SQL to manipulate the responder location, tracks, and assignment tables.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48235.json
- https://github.com/openises/tickets/releases/tag/v3.44.2
- https://nvd.nist.gov/vuln/detail/CVE-2026-48235
- https://www.vulncheck.com/advisories/open-ises-tickets-sql-injection-via-incs-remotes-inc-php-multiple-parameters
- https://github.com/openises/tickets/commit/ecfeb406a016766cae81c749e14b5145a9f2dbff
