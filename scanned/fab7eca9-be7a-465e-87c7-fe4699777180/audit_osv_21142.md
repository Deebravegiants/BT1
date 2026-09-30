# [C] CVE-2021-40887

## Summary
Severity: Critical
Advisory: CVE-2021-40887
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-10-11
Source: https://osv.dev/vulnerability/CVE-2021-40887
Type: osv

## Details
Projectsend version r1295 is affected by a directory traversal vulnerability. Because of lacking sanitization input for files[] parameter, an attacker can add ../ to move all PHP files or any file on the system that has permissions to /upload/files/ folder.

## References
- https://github.com/projectsend/projectsend/issues/994
