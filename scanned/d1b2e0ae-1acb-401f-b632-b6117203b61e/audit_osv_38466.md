# [H] HomeBox has Unauthorized API Access via Retained defaultGroup ID After Group Access Revocation

## Summary
Severity: High
Advisory: CVE-2026-40196
Aliases: GHSA-6pvm-v73p-p6m9
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-04-17
Source: https://osv.dev/vulnerability/CVE-2026-40196
Type: osv

## Details
HomeBox is a home inventory and organization system. Versions prior to 0.25.0 contain a vulnerability where the defaultGroup ID remained permanently assigned to a user after being invited to a group, even after their access to that group was revoked. While the web interface correctly enforced the access revocation and prevented the user from viewing or modifying the group's contents, the API did not. Because the original group ID persisted as the user's defaultGroup, and this value was not properly validated when the X-Tenant header was omitted, the user could still perform full CRUD operations on the group's collections through the API, bypassing the intended access controls. This issue has been fixed in version 0.25.0.

## References
- https://github.com/sysadminsmedia/homebox/releases/tag/v0.25.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40196.json
- https://github.com/sysadminsmedia/homebox/security/advisories/GHSA-6pvm-v73p-p6m9
- https://nvd.nist.gov/vuln/detail/CVE-2026-40196
