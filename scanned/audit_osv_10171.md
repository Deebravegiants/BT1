# [C] CVE-2017-14145

## Summary
Severity: Critical
Advisory: CVE-2017-14145
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-09-05
Source: https://osv.dev/vulnerability/CVE-2017-14145
Type: osv

## Details
HelpDEZk 1.1.1 has SQL Injection in app\modules\admin\controllers\loginController.php via the admin/login/getWarningInfo/id/ PATH_INFO, related to the selectWarning function.

## References
- https://github.com/M4ple/vulnerability/blob/master/helpdezk_sql/helpdezk_sql_injection.md
