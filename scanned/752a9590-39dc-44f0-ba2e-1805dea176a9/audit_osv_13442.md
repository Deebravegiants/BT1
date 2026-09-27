# [H] CVE-2018-19894

## Summary
Severity: High
Advisory: CVE-2018-19894
CVSS: 7.2 (CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-12-06
Source: https://osv.dev/vulnerability/CVE-2018-19894
Type: osv

## Details
ThinkCMF X2.2.2 has SQL Injection via the functions check() and delete() in CommentadminController.class.php and is exploitable with the manager privilege via the ids[] parameter in a commentadmin action.

## References
- https://github.com/thinkcmf/cmfx/issues/26
