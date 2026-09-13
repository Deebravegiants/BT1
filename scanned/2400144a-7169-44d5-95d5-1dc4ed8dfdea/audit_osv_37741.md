# [C] Roxy-WI has SQL Injection in haproxy_section_save Endpoint via Unsanitized server_ip Parameter

## Summary
Severity: Critical
Advisory: CVE-2026-33078
Aliases: GHSA-jmj9-2c4q-849j
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P)
Published: 2026-04-24
Source: https://osv.dev/vulnerability/CVE-2026-33078
Type: osv

## Details
Roxy-WI is a web interface for managing Haproxy, Nginx, Apache and Keepalived servers. Versions prior to 8.2.6.4 have a SQL injection vulnerability in the haproxy_section_save function in app/routes/config/routes.py. The server_ip parameter, sourced from the URL path, is passed unsanitized through multiple function calls and ultimately interpolated into a SQL query string using Python string formatting, allowing attackers to execute arbitrary SQL commands. Version 8.2.6.4 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33078.json
- https://github.com/roxy-wi/roxy-wi/security/advisories/GHSA-jmj9-2c4q-849j
- https://nvd.nist.gov/vuln/detail/CVE-2026-33078
- https://github.com/roxy-wi/roxy-wi/commit/aecc7971959092fa93e93531f1ffcde33524b031
