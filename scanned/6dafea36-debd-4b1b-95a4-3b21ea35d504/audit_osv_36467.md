# [M] OpenProject users with "View Members" permission in any project can view all Group memberships

## Summary
Severity: Medium
Advisory: CVE-2026-23721
Aliases: GHSA-vj77-wrc2-5h5h
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-01-19
Source: https://osv.dev/vulnerability/CVE-2026-23721
Type: osv

## Details
OpenProject is an open-source, web-based project management software. When using groups in OpenProject to manage users, the group members should only be visible to users that have the View Members permission in any project that the group is also a member of. Prior to versions 17.0.1 and 16.6.5, due to a failed permission check, if a user had the View Members permission in any project, they could enumerate all Groups and view which other users are part of the group. The issue has been fixed in OpenProject 17.0.1 and 16.6.5. No known workarounds are available.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23721.json
- https://github.com/opf/openproject/security/advisories/GHSA-vj77-wrc2-5h5h
- https://nvd.nist.gov/vuln/detail/CVE-2026-23721
