# [H] CVE-2019-11446

## Summary
Severity: High
Advisory: CVE-2019-11446
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-04-22
Source: https://osv.dev/vulnerability/CVE-2019-11446
Type: osv

## Details
An issue was discovered in ATutor through 2.2.4. It allows the user to run commands on the server with the teacher user privilege. The Upload Files section in the File Manager field contains an arbitrary file upload vulnerability via upload.php. The $IllegalExtensions value only lists lowercase (and thus .phP is a bypass), and omits .shtml and .phtml.

## References
- http://pentest.com.tr/exploits/ATutor-2-2-4-file-manager-Remote-Code-Execution-Injection-Metasploit.html
- https://www.exploit-db.com/exploits/46691/
