# [H] CVE-2020-28874

## Summary
Severity: High
Advisory: CVE-2020-28874
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2021-01-26
Source: https://osv.dev/vulnerability/CVE-2020-28874
Type: osv

## Details
reset-password.php in ProjectSend before r1295 allows remote attackers to reset a password because of incorrect business logic. Errors are not properly considered (an invalid token parameter).

## References
- https://github.com/projectsend/projectsend/releases/tag/r1295
- https://github.com/projectsend/projectsend/commit/440204734e9a1687cb9887e1c887173d23c5a93e
- https://github.com/projectsend/projectsend/commits/master
- https://github.com/varandinawer/CVE-2020-28874
