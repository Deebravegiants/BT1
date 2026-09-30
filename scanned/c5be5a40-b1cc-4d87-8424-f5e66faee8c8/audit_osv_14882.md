# [H] CVE-2019-12170

## Summary
Severity: High
Advisory: CVE-2019-12170
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-05-17
Source: https://osv.dev/vulnerability/CVE-2019-12170
Type: osv

## Details
ATutor through 2.2.4 is vulnerable to arbitrary file uploads via the mods/_core/backups/upload.php (aka backup) component. This may result in remote command execution. An attacker can use the instructor account to fully compromise the system using a crafted backup ZIP archive. This will allow for PHP files to be written to the web root, and for code to execute on the remote server.

## References
- http://packetstormsecurity.com/files/153869/ATutor-2.2.4-Backup-Remote-Command-Execution.html
- http://incidentsecurity.com/atutor-2-2-4-backup-remote-command-execution/
- https://github.com/fuzzlove/ATutor-Instructor-Backup-Arbitrary-File
