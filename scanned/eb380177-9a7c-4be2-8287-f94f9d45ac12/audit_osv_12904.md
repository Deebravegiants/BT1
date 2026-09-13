# [M] CVE-2018-16251

## Summary
Severity: Medium
Advisory: CVE-2018-16251
CVSS: 4.3 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2019-06-20
Source: https://osv.dev/vulnerability/CVE-2018-16251
Type: osv

## Details
A "search for user discovery" injection issue exists in Creatiwity wityCMS 0.6.2 via the "Utilisateur" menu. No input parameters are filtered, e.g., the /admin/user/users Nickname, email, firstname, lastname, and groupe parameters.

## References
- https://github.com/Creatiwity/wityCMS/issues/157
