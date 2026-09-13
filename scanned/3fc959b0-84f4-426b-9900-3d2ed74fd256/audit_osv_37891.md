# [M] Chamilo LMS has REST API PII Exposure via get_user_info_from_username

## Summary
Severity: Medium
Advisory: CVE-2026-33708
Aliases: GHSA-qwch-82q9-q999
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-04-10
Source: https://osv.dev/vulnerability/CVE-2026-33708
Type: osv

## Details
Chamilo LMS is a learning management system. Prior to 1.11.38, the get_user_info_from_username REST API endpoint returns personal information (email, first name, last name, user ID, active status) of any user to any authenticated user, including students. There is no authorization check. This vulnerability is fixed in 1.11.38.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33708.json
- https://github.com/chamilo/chamilo-lms/security/advisories/GHSA-qwch-82q9-q999
- https://nvd.nist.gov/vuln/detail/CVE-2026-33708
- https://github.com/chamilo/chamilo-lms/commit/4a119f93abbfba6fe833580f2463c8d4afa500c2
