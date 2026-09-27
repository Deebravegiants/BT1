# [C] CVE-2019-16114

## Summary
Severity: Critical
Advisory: CVE-2019-16114
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-09-09
Source: https://osv.dev/vulnerability/CVE-2019-16114
Type: osv

## Details
In ATutor 2.2.4, an unauthenticated attacker can change the application settings and force it to use his crafted database, which allows him to gain access to the application. Next, he can change the directory that the application uploads files to, which allows him to achieve remote code execution. This occurs because install/include/header.php does not restrict certain changes (to db_host, db_login, db_password, and content_dir) within install/include/step5.php.

## References
- https://github.com/atutor/ATutor/commits/master
- https://github.com/MostafaSoliman/Security-Advisories/blob/master/CVE-2019-16114/README.md
