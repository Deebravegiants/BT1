# [H] CVE-2020-28693

## Summary
Severity: High
Advisory: CVE-2020-28693
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-11-16
Source: https://osv.dev/vulnerability/CVE-2020-28693
Type: osv

## Details
An unrestricted file upload issue in HorizontCMS 1.0.0-beta allows an authenticated remote attacker to upload PHP code through a zip file by uploading a theme, and executing the PHP file via an HTTP GET request to /themes/<php_file_name>

## References
- https://github.com/ttimot24/HorizontCMS/issues/21
- https://github.com/jkana/HorizontCMS-1.0.0-beta-shell-upload
