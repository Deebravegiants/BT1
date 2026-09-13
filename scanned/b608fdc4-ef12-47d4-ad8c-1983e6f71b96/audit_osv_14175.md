# [M] CVE-2018-7663

## Summary
Severity: Medium
Advisory: CVE-2018-7663
CVSS: 6.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2018-03-05
Source: https://osv.dev/vulnerability/CVE-2018-7663
Type: osv

## Details
An issue was discovered in resources/views/layouts/app.blade.php in Voten.co before 2017-08-25. An unescaped template literal in the bio field of a user profile (resources/views/layouts/app.blade.php) allows for server-side template injection of arbitrary JavaScript.

## References
- https://github.com/voten-co/voten/commit/ee6a322568166e28465da075159a6d4adbf74d53
- https://github.com/spencerdodd/public-writeups/blob/master/CVE-2018-7663/README.md
