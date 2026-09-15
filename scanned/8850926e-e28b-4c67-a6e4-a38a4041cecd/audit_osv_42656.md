# [M] OpenIM Server v3.8.3 Missing Authorization on User and Group Enumeration Endpoints

## Summary
Severity: Medium
Advisory: CVE-2026-69115
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-69115
Type: osv

## Details
OpenIM Server v3.8.3 contains a missing authorization vulnerability that allows any authenticated user to access admin-only management API endpoints by submitting POST requests with a regular user bearer token to /user/get_users, /user/get_all_users_uid, and /group/get_groups. Attackers can exploit the absent authverify.CheckAdmin() call in the GetPaginationUsers, GetAllUserID, and GetGroups handlers to enumerate all platform user accounts including userIDs, nicknames, and manager level flags, as well as all groups including private groups the user has never joined, exposing group names, owner IDs, and member counts.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/69xxx/CVE-2026-69115.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-69115
- https://www.vulncheck.com/advisories/openim-server-missing-authorization-on-user-and-group-enumeration-endpoints
- https://github.com/openimsdk/open-im-server/issues/3778
- https://github.com/openimsdk/open-im-server/pull/3781
- https://github.com/openimsdk/open-im-server/commit/193870b2f938278b27a2d8347bd7e4db5f8f9dfc
- https://github.com/openimsdk/open-im-server
