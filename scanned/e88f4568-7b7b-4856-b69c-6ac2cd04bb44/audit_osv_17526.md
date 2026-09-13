# [H] CVE-2020-15884

## Summary
Severity: High
Advisory: CVE-2020-15884
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-07-23
Source: https://osv.dev/vulnerability/CVE-2020-15884
Type: osv

## Details
A SQL injection vulnerability in TableQuery.php in MunkiReport before 5.6.3 allows attackers to execute arbitrary SQL commands via the order[0][dir] field on POST requests to /datatables/data.

## References
- https://github.com/munkireport/munkireport-php/releases
- https://github.com/munkireport/munkireport-php/releases/tag/v5.6.3
- https://github.com/munkireport/munkireport-php/wiki/20200722-SQL-Injection-In-Datatables-Order-By-In-Post-Body
