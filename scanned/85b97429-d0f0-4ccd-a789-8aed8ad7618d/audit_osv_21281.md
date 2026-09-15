# [C] CVE-2021-41679

## Summary
Severity: Critical
Advisory: CVE-2021-41679
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-11-30
Source: https://osv.dev/vulnerability/CVE-2021-41679
Type: osv

## Details
A SQL injection vulnerability exists in version 8.0 of openSIS when MySQL or MariaDB is used as the application database. An attacker can then issue the SQL command through the /opensis/modules/grades/InputFinalGrades.php, period parameter.

## References
- https://github.com/OS4ED/openSIS-Classic/issues/204
