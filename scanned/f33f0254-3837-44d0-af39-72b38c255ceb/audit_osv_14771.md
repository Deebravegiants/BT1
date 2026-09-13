# [H] CVE-2019-11378

## Summary
Severity: High
Advisory: CVE-2019-11378
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-04-20
Source: https://osv.dev/vulnerability/CVE-2019-11378
Type: osv

## Details
An issue was discovered in ProjectSend r1053. upload-process-form.php allows finished_files[]=../ directory traversal. It is possible for users to read arbitrary files and (potentially) access the supporting database, delete arbitrary files, access user passwords, or run arbitrary code.

## References
- http://www.securityfocus.com/bid/108069
- https://github.com/projectsend/projectsend/issues/700
