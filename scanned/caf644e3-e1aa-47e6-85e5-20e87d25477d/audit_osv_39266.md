# [M] Pi.Alert: Web Interface Vulnerable to Unauthenticated Blind SQL Injection

## Summary
Severity: Medium
Advisory: CVE-2026-44886
Aliases: GHSA-m929-j7w8-334j
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-44886
Type: osv

## Details
Pi.Alert is a WIFI / LAN intruder detector with web service monitoring. From 2024-06-29 to before 2026-05-07, the web application endpoint is vulnerable to SQL injection. The /pialert/php/server/devices.php route accepts requests from unauthenticated users when the action URL parameter is set to getDevicesTotals. The scansource URL parameter is then injected in a SQL query. This vulnerability is fixed in 2026-05-07.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44886.json
- https://github.com/leiweibau/Pi.Alert/security/advisories/GHSA-m929-j7w8-334j
- https://nvd.nist.gov/vuln/detail/CVE-2026-44886
- https://projectblack.io/blog/pi-alert-unauthenticated-sql-injection
