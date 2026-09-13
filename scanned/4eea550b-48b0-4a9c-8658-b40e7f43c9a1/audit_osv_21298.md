# [M] CVE-2021-41843

## Summary
Severity: Medium
Advisory: CVE-2021-41843
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-12-17
Source: https://osv.dev/vulnerability/CVE-2021-41843
Type: osv

## Details
An authenticated SQL injection issue in the calendar search function of OpenEMR 6.0.0 before patch 3 allows an attacker to read data from all tables of the database via the parameter provider_id, as demonstrated by the /interface/main/calendar/index.php?module=PostCalendar&func=search URI.

## References
- http://packetstormsecurity.com/files/165301/OpenEMR-6.0.0-6.1.0-dev-SQL-Injection.html
- http://seclists.org/fulldisclosure/2021/Dec/38
- https://trovent.github.io/security-advisories/TRSA-2109-01/TRSA-2109-01.txt
- https://trovent.io/security-advisory-2109-01
