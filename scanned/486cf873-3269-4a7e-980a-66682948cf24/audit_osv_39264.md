# [M] JumpServer: Privilege Overwrite via Organization Invite Logic Flaw

## Summary
Severity: Medium
Advisory: CVE-2026-44846
Aliases: GHSA-j836-99w5-523r
CVSS: 6.2 (CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:L)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2026-44846
Type: osv

## Details
JumpServer is an open source bastion host and an operation and maintenance security audit system. Prior to 4.10.17, a user with the users.invite_user permission can submit an existing member to POST /api/v1/users/users/invite/, causing the organization invitation logic in apps/users/api/user.py to execute user.org_roles.set(org_roles) and replace the member's existing organization roles, which can escalate privileges or downgrade administrators. This issue is fixed in version 4.10.17.

## References
- https://github.com/jumpserver/jumpserver/releases/tag/v4.10.17
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44846.json
- https://github.com/jumpserver/jumpserver/security/advisories/GHSA-j836-99w5-523r
- https://nvd.nist.gov/vuln/detail/CVE-2026-44846
- https://github.com/jumpserver/jumpserver/commit/1803be11a410eb99cd171d47053b697a119c4a50
- https://github.com/jumpserver/jumpserver/pull/16662
