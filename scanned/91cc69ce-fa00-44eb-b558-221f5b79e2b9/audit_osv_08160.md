# [H] CVE-2016-10753

## Summary
Severity: High
Advisory: CVE-2016-10753
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-05-24
Source: https://osv.dev/vulnerability/CVE-2016-10753
Type: osv

## Details
e107 2.1.2 allows PHP Object Injection with resultant SQL injection, because usersettings.php uses unserialize without an HMAC.

## References
- https://demo.ripstech.com/projects/e107_2.1.2
- https://blog.ripstech.com/2016/e107-sql-injection-through-object-injection/
