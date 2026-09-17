# [M] CVE-2018-15918

## Summary
Severity: Medium
Advisory: CVE-2018-15918
CVSS: 5.4 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2018-09-05
Source: https://osv.dev/vulnerability/CVE-2018-15918
Type: osv

## Details
An issue was discovered in Jorani 0.6.5. SQL Injection (error-based) allows a user of the application without permissions to read and modify sensitive information from the database used by the application via the startdate or enddate parameter to leaves/validate.

## References
- https://www.exploit-db.com/exploits/45340/
- https://github.com/bbalet/jorani/issues/254
- https://hackpuntes.com/cve-2018-15918-jorani-leave-management-system-0-6-5-sql-injection/
