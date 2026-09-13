# [H] CVE-2020-10190

## Summary
Severity: High
Advisory: CVE-2020-10190
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-03-09
Source: https://osv.dev/vulnerability/CVE-2020-10190
Type: osv

## Details
An issue was discovered in MunkiReport before 5.3.0. An authenticated user could achieve SQL Injection in app/models/tablequery.php by crafting a special payload on the /datatables/data endpoint.

## References
- https://github.com/munkireport/munkireport-php/releases
- https://github.com/munkireport/munkireport-php/wiki/20200309-Authenticated-SQL-injection
