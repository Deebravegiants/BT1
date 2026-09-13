# [H] Chamilo LMS has a REST API Self-Privilege Escalation (Student → Teacher)

## Summary
Severity: High
Advisory: CVE-2026-33706
Aliases: GHSA-3gqc-xr75-pcpw
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:N)
Published: 2026-04-10
Source: https://osv.dev/vulnerability/CVE-2026-33706
Type: osv

## Details
Chamilo LMS is a learning management system. Prior to 1.11.38, any authenticated user with a REST API key can modify their own status field via the update_user_from_username endpoint. A student (status=5) can change their status to Teacher/CourseManager (status=1), gaining course creation and management privileges. This vulnerability is fixed in 1.11.38.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33706.json
- https://github.com/chamilo/chamilo-lms/security/advisories/GHSA-3gqc-xr75-pcpw
- https://nvd.nist.gov/vuln/detail/CVE-2026-33706
- https://github.com/chamilo/chamilo-lms/commit/0acf8a196307c66c049f97f5ff76cf21c4a08127
