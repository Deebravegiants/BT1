# [H] Koha SQL Injection via order_by and {order}_ovalue Parameters in guided_reports.pl

## Summary
Severity: High
Advisory: CVE-2026-71288
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-71288
Type: osv

## Details
Koha's guided report builder (reports/guided_reports.pl) reads the CGI parameter and, for each value, a dynamically-named parameter, and concatenates both directly into an SQL ORDER BY clause with no allowlist or validation. Since ORDER BY columns cannot be bound via prepared-statement placeholders, this requires an explicit allowlist, which does not exist.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/71xxx/CVE-2026-71288.json
- https://github.com/Koha-Community/Koha
- https://github.com/Koha-Community/Koha/blob/master/reports/guided_reports.pl
- https://nvd.nist.gov/vuln/detail/CVE-2026-71288
