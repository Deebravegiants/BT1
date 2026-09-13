# [M] OpenProject: Relations API Filter Bypasses Visibility Scope, Leaking Cross-Project Work Package Subjects

## Summary
Severity: Medium
Advisory: CVE-2026-44736
Aliases: GHSA-p9gq-hrgh-2645
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-06-26
Source: https://osv.dev/vulnerability/CVE-2026-44736
Type: osv

## Details
OpenProject is open-source, web-based project management software. Prior to 17.4.0, the GET /api/v3/relations endpoint allows any authenticated user to retrieve relations — and the subject (title) of work packages they have no permission to view — by supplying an arbitrary work package ID in the involved, fromId, or toId filter. This bypasses the Relation.visible scope due to a flawed performance optimization in RelationQuery. This vulnerability is fixed in 17.4.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44736.json
- https://github.com/opf/openproject/security/advisories/GHSA-p9gq-hrgh-2645
- https://nvd.nist.gov/vuln/detail/CVE-2026-44736
