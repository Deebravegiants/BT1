# [H] CVE-2018-20329

## Summary
Severity: High
Advisory: CVE-2018-20329
CVSS: 8.1 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2018-12-21
Source: https://osv.dev/vulnerability/CVE-2018-20329
Type: osv

## Details
Chamilo LMS version 1.11.8 contains a main/inc/lib/CoursesAndSessionsCatalog.class.php SQL injection, allowing users with access to the sessions catalogue (which may optionally be made public) to extract and/or modify database information.

## References
- https://github.com/chamilo/chamilo-lms/commit/bfa1eccfabb457b800618d9d115f12dc614a55df
- https://support.chamilo.org/projects/1/wiki/Security_issues#Issue-33-2018-12-13-Moderate-risk-high-impact-SQL-Injection
