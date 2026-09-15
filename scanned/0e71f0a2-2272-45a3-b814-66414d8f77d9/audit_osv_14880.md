# [H] CVE-2019-12169

## Summary
Severity: High
Advisory: CVE-2019-12169
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-06-03
Source: https://osv.dev/vulnerability/CVE-2019-12169
Type: osv

## Details
ATutor 2.2.4 allows Arbitrary File Upload and Directory Traversal, resulting in remote code execution via a ".." pathname in a ZIP archive to the mods/_core/languages/language_import.php (aka Import New Language) or mods/_standard/patcher/index_admin.php (aka Patcher) component.

## References
- https://github.com/fuzzlove
- http://incidentsecurity.com/atutor-2-2-4-language_import-arbitrary-file-upload-rce/
- http://packetstormsecurity.com/files/153870/ATutor-2.2.4-Arbitrary-File-Upload-Command-Execution.html
- http://packetstormsecurity.com/files/158246/ATutor-2.2.4-Directory-Traversal-Remote-Code-Execution.html
- https://github.com/fuzzlove/ATutor-2.2.4-Language-Exploit
