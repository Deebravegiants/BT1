# [C] CVE-2021-35414

## Summary
Severity: Critical
Advisory: CVE-2021-35414
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-12-03
Source: https://osv.dev/vulnerability/CVE-2021-35414
Type: osv

## Details
Chamilo LMS v1.11.x was discovered to contain a SQL injection via the doc parameter in main/plagiarism/compilatio/upload.php.

## References
- https://github.com/andrejspuler/writeups/tree/main/chamilo-lms#unauthenticated-sql-injection-2-in-plugin
- https://github.com/andrejspuler/writeups/tree/main/chamilo-lms#unauthenticated-sql-injection-in-compilatio-module
- https://github.com/chamilo/chamilo-lms/commit/36149c1ff99973840a809bb865f23e1b23d6df00
- https://github.com/chamilo/chamilo-lms/commit/6a98e32bb04aa66cbd0d29ad74d7d20cc7e7e9c5
- https://github.com/chamilo/chamilo-lms/commit/f398b5b45c019f873a54fe25c815dbaaf963728b
- https://support.chamilo.org/projects/1/wiki/Security_issues#Issue-59-2021-05-13-High-impact-low-risk-Unauthenticated-SQL-injection-vulnerability-when-a-module-is-enabled
- https://support.chamilo.org/projects/1/wiki/Security_issues#Issue-65-2021-05-15-High-impact-very-high-risk-Unauthenticated-SQL-injection-in-plugin
