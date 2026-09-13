# [C] CVE-2018-18892

## Summary
Severity: Critical
Advisory: CVE-2018-18892
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-11-01
Source: https://osv.dev/vulnerability/CVE-2018-18892
Type: osv

## Details
MiniCMS 1.10 allows execution of arbitrary PHP code via the install.php sitename parameter, which affects the site_name field in mc_conf.php.

## References
- https://github.com/AvaterXXX/MiniCms/blob/master/Command%20Execution.md
- https://www.patec.cn/newsshow.php?cid=24&id=135
