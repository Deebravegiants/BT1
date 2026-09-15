# [H] CVE-2021-35413

## Summary
Severity: High
Advisory: CVE-2021-35413
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-12-03
Source: https://osv.dev/vulnerability/CVE-2021-35413
Type: osv

## Details
A remote code execution (RCE) vulnerability in course_intro_pdf_import.php of Chamilo LMS v1.11.x allows authenticated attackers to execute arbitrary code via a crafted .htaccess file.

## References
- https://github.com/andrejspuler/writeups/tree/main/chamilo-lms#authenticated-remote-code-execution-in-import-file
- https://github.com/chamilo/chamilo-lms/commit/2e5c004b57d551678a1815500ef91524ba7bb757
- https://github.com/chamilo/chamilo-lms/commit/905a21037ebc9bc5369f0fb380177cb56f496f5c
- https://support.chamilo.org/projects/1/wiki/Security_issues#Issue-66-2021-05-21-High-impact-very-low-risk-Authenticated-RCE-in-accessory-script
