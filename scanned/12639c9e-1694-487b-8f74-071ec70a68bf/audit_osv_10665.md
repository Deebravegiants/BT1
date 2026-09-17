# [H] CVE-2017-18048

## Summary
Severity: High
Advisory: CVE-2017-18048
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-01-23
Source: https://osv.dev/vulnerability/CVE-2017-18048
Type: osv

## Details
Monstra CMS 3.0.4 allows users to upload arbitrary files, which leads to remote command execution on the server, for example because .php (lowercase) is blocked but .PHP (uppercase) is not.

## References
- https://github.com/monstra-cms/monstra/issues/426
- https://blogs.securiteam.com/index.php/archives/3559
- https://securityprince.blogspot.in/2017/12/monstra-cms-304-arbitrary-file-upload.html
- https://www.exploit-db.com/exploits/43348/
