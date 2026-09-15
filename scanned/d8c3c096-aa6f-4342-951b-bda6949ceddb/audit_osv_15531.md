# [H] CVE-2019-16980

## Summary
Severity: High
Advisory: CVE-2019-16980
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-10-21
Source: https://osv.dev/vulnerability/CVE-2019-16980
Type: osv

## Details
In FusionPBX up to v4.5.7, the file app\call_broadcast\call_broadcast_edit.php uses an unsanitized "id" variable coming from the URL in an unparameterized SQL query, leading to SQL injection.

## References
- https://resp3ctblog.wordpress.com/2019/10/19/fusionpbx-sqli-1/
- https://github.com/fusionpbx/fusionpbx/commit/6fe372b3d4bb7ff07778d152886edcecc045c7ec
