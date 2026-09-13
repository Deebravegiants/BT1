# [H] CVE-2020-10057

## Summary
Severity: High
Advisory: CVE-2020-10057
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-03-04
Source: https://osv.dev/vulnerability/CVE-2020-10057
Type: osv

## Details
GeniXCMS 1.1.7 is vulnerable to user privilege escalation due to broken access control. This issue exists because of an incomplete fix for CVE-2015-2680, in which "token" is used as a CSRF protection mechanism, but without validation that "token" is associated with an administrative user.

## References
- https://github.com/J3rryBl4nks/GenixCMS/blob/master/CreateAdminBAC.md
