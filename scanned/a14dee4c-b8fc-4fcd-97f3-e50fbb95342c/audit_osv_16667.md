# [C] CVE-2019-9002

## Summary
Severity: Critical
Advisory: CVE-2019-9002
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-02-22
Source: https://osv.dev/vulnerability/CVE-2019-9002
Type: osv

## Details
An issue was discovered in Tiny Issue 1.3.1 and pixeline Bugs through 1.3.2c. install/config-setup.php allows remote attackers to execute arbitrary PHP code via the database_host parameter if the installer remains present in its original directory after installation is completed.

## References
- https://github.com/pixeline/bugs/commit/9d2d3fcdea22e94f7b497f6ed83791ab3a31ee41
- https://github.com/mikelbring/tinyissue/issues/237
