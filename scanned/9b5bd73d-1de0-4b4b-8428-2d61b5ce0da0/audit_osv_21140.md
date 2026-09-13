# [H] CVE-2021-40884

## Summary
Severity: High
Advisory: CVE-2021-40884
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2021-10-11
Source: https://osv.dev/vulnerability/CVE-2021-40884
Type: osv

## Details
Projectsend version r1295 is affected by sensitive information disclosure. Because of not checking authorization in ids parameter in files-edit.php and id parameter in process.php function, a user with uploader role can download and edit all files of users in application.

## References
- https://github.com/projectsend/projectsend/issues/992
