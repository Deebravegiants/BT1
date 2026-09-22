# [H] CVE-2017-15880

## Summary
Severity: High
Advisory: CVE-2017-15880
CVSS: 7.2 (CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-10-24
Source: https://osv.dev/vulnerability/CVE-2017-15880
Type: osv

## Details
SQL injection vulnerability vulnerability in the EyesOfNetwork web interface (aka eonweb) 5.1-0 allows remote authenticated administrators to execute arbitrary SQL commands via the group_name parameter to module/admin_group/add_modify_group.php (for insert_group and update_group).

## References
- https://github.com/jsj730sos/cve/blob/master/Eonweb_module_admin_group_add_modify_group.php%20SQLi
- https://github.com/jsj730sos/cve/blob/master/Eonweb_module_admin_group_add_modify_group.php-update_group-SQL%20injection%20vulnerability
