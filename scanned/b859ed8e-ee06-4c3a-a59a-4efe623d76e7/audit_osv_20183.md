# [H] CVE-2021-31933

## Summary
Severity: High
Advisory: CVE-2021-31933
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-04-30
Source: https://osv.dev/vulnerability/CVE-2021-31933
Type: osv

## Details
A remote code execution vulnerability exists in Chamilo through 1.11.14 due to improper input sanitization of a parameter used for file uploads, and improper file-extension filtering for certain filenames (e.g., .phar or .pht). A remote authenticated administrator is able to upload a file containing arbitrary PHP code into specific directories via main/inc/lib/fileUpload.lib.php directory traversal to achieve PHP code execution.

## References
- https://github.com/chamilo/chamilo-lms/commit/229302139e8d23bf6862183cf219b967f6e2fbc1
- https://github.com/chamilo/chamilo-lms/commit/f65d065061a77bb2e84f73217079ce3998cf3453
- https://support.chamilo.org/projects/1/wiki/Security_issues#Issue-48-2021-04-17-Critical-impact-high-risk-Remote-Code-Execution
- http://packetstormsecurity.com/files/162572/Chamilo-LMS-1.11.14-Remote-Code-Execution.html
