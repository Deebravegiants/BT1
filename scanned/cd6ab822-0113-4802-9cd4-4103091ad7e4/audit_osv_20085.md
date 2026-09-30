# [H] CVE-2021-30141

## Summary
Severity: High
Advisory: CVE-2021-30141
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-04-05
Source: https://osv.dev/vulnerability/CVE-2021-30141
Type: osv

## Details
Module/Settings/UserExport.php in Friendica through 2021.01 allows settings/userexport to be used by anonymous users, as demonstrated by an attempted access to an array offset on a value of type null, and excessive memory consumption. NOTE: the vendor states "the feature still requires a valid authentication cookie even if the route is accessible to non-logged users.

## References
- https://github.com/friendica/friendica/pull/10113/commits/acbcc56754121ba080eac5b6fdf69e64ed7fe453
- https://github.com/friendica/friendica/issues/10110
