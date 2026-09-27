# [H] CVE-2019-11445

## Summary
Severity: High
Advisory: CVE-2019-11445
CVSS: 7.2 (CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-04-22
Source: https://osv.dev/vulnerability/CVE-2019-11445
Type: osv

## Details
OpenKM 6.3.2 through 6.3.7 allows an attacker to upload a malicious JSP file into the /okm:root directories and move that file to the home directory of the site, via frontend/FileUpload and admin/repository_export.jsp. This is achieved by interfering with the Filesystem path control in the admin's Export field. As a result, attackers can gain remote code execution through the application server with root privileges.

## References
- https://pentest.com.tr/exploits/OpenKM-DM-6-3-7-Remote-Command-Execution-Metasploit.html
- https://www.exploit-db.com/exploits/46526
