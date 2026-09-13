# [M] OpenProject: Improper Access Control through /api/v3/custom_options/:id via Path "id" leads to Sensitive Data Exposure

## Summary
Severity: Medium
Advisory: CVE-2026-67528
Aliases: GHSA-wr3w-qchj-p4cm
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/CVE-2026-67528
Type: osv

## Details
OpenProject is open-source, web-based project management software. Prior to 17.6.0, GET /api/v3/custom_options/:id resolved CustomOption records by global numeric id and allowed UserCustomField and GroupCustomField options without checking visible(current_user), so authenticated non-admin users could enumerate sequential custom option ids and read labels belonging to admin_only user or group custom fields. This issue is fixed in 17.6.0.

## References
- https://github.com/opf/openproject/releases/tag/v17.6.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/67xxx/CVE-2026-67528.json
- https://github.com/opf/openproject/security/advisories/GHSA-wr3w-qchj-p4cm
- https://nvd.nist.gov/vuln/detail/CVE-2026-67528
- https://github.com/opf/openproject/commit/a13fa079bc8040449570384c19f2d98f637179f1
