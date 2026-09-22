# [C] CVE-2020-23359

## Summary
Severity: Critical
Advisory: CVE-2020-23359
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-01-27
Source: https://osv.dev/vulnerability/CVE-2020-23359
Type: osv

## Details
WeBid 1.2.2 admin/newuser.php has an issue with password rechecking during registration because it uses a loose comparison to check the identicalness of two passwords. Two non-identical passwords can still bypass the check.

## References
- https://github.com/renlok/WeBid/issues/530
