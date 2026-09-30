# [C] CVE-2018-12649

## Summary
Severity: Critical
Advisory: CVE-2018-12649
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-06-22
Source: https://osv.dev/vulnerability/CVE-2018-12649
Type: osv

## Details
An issue was discovered in app/Controller/UsersController.php in MISP 2.4.92. An adversary can bypass the brute-force protection by using a PUT HTTP method instead of a POST HTTP method in the login part, because this protection was only covering POST requests.

## References
- https://github.com/MISP/MISP/commit/6ffacc1e239930e0e8464d0ca16e432e26cf36a9
