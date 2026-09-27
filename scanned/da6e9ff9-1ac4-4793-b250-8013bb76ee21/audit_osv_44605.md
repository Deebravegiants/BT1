# [H] ntopng's Missing Authorization in REST API Allows Non-Admin Users to Delete and Rename Arbitrary Tags

## Summary
Severity: High
Advisory: CVE-2026-84989
Aliases: GHSA-43p9-5758-wwq8
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:L)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-84989
Type: osv

## Details
ntopng is a web-based network traffic monitoring application. In versions 6.7.0 through 6.7.260717, two REST v2 endpoints that manage ntopng's tag/badge feature — `POST /lua/rest/v2/delete/tag/tag.lua` and `POST /lua/rest/v2/edit/tag/tag.lua` — perform no authorization check at all. Any authenticated user, including a non-administrator ("unprivileged") account, can delete or rename any tag in the system, including tags created by an administrator. Version 6.7.260718 contains a fix.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/84xxx/CVE-2026-84989.json
- https://github.com/ntop/ntopng/security/advisories/GHSA-43p9-5758-wwq8
- https://nvd.nist.gov/vuln/detail/CVE-2026-84989
- https://github.com/ntop/ntopng/commit/0e41f24b367fb9caf750459da67827326e3289e8
