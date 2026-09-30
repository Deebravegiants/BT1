# [H] CVE-2020-8639

## Summary
Severity: High
Advisory: CVE-2020-8639
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-04-03
Source: https://osv.dev/vulnerability/CVE-2020-8639
Type: osv

## Details
An unrestricted file upload vulnerability in keywordsImport.php in TestLink 1.9.20 allows remote attackers to execute arbitrary code by uploading a file with an executable extension. This allows an authenticated attacker to upload a malicious file (containing PHP code to execute operating system commands) to a publicly accessible directory of the application.

## References
- https://ackcent.com/blog/testlink-1.9.20-unrestricted-file-upload-and-sql-injection/
- https://github.com/TestLinkOpenSourceTRMS/testlink-code/commit/57d81ae350d569c5c95087997fe051c49e14516d
- http://packetstormsecurity.com/files/161401/TestLink-1.9.20-Shell-Upload.html
