# [H] Chamilo LMS has Privilege Escalation via API User Role Modification

## Summary
Severity: High
Advisory: CVE-2026-40291
Aliases: GHSA-7phx-w897-4c9x
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-14
Source: https://osv.dev/vulnerability/CVE-2026-40291
Type: osv

## Details
Chamilo LMS is an open-source learning management system. In versions prior to 2.0.0-RC.3, an insecure direct object modification vulnerability in the PUT /api/users/{id} endpoint allows any authenticated user with ROLE_STUDENT to escalate their privileges to ROLE_ADMIN by modifying the roles field on their own user record. The API Platform security expression is_granted('EDIT', object) only verifies record ownership, and the roles field is included in the writable serialization group, enabling any user to set arbitrary roles such as ROLE_ADMIN. Successful exploitation grants full administrative control of the platform, including access to all courses, user data, grades, and administrative settings. This issue has been fixed in version 2.0.0-RC.3.

## References
- https://github.com/chamilo/chamilo-lms/releases/tag/v2.0.0-RC.3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40291.json
- https://github.com/chamilo/chamilo-lms/security/advisories/GHSA-7phx-w897-4c9x
- https://nvd.nist.gov/vuln/detail/CVE-2026-40291
