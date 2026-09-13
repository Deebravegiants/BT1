# [H] CVE-2018-19520

## Summary
Severity: High
Advisory: CVE-2018-19520
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-11-25
Source: https://osv.dev/vulnerability/CVE-2018-19520
Type: osv

## Details
An issue was discovered in SDCMS 1.6 with PHP 5.x. app/admin/controller/themecontroller.php uses a check_bad function in an attempt to block certain PHP functions such as eval, but does not prevent use of preg_replace 'e' calls, allowing users to execute arbitrary code by leveraging access to admin template management.

## References
- https://blog.whiterabbitxyj.com/cve/SDCMS_1.6_code_execution.doc
- https://github.com/WhiteRabbitc/WhiteRabbitc.github.io/blob/master/cve/SDCMS_1.6_code_execution.doc
