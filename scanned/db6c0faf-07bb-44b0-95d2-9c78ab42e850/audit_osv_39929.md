# [H] Activepieces: Cross-tenant data exposure and code injection via the Code piece sandbox cache

## Summary
Severity: High
Advisory: CVE-2026-48499
Aliases: GHSA-5h2x-g6m3-grmq
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:H/SI:H/SA:N)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/CVE-2026-48499
Type: osv

## Details
Activepieces is an open source AI workflow automation platform. Prior to 0.84.0, an unsanitized path segment in the Code piece sandbox can let an authenticated flow author reach read-write cached flow and code files belonging to other tenants on the same worker, exposing embedded data and allowing modified code to execute on a victim tenant's next flow run. This issue is fixed in version 0.84.0.

## References
- https://github.com/activepieces/activepieces/releases/tag/0.84.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48499.json
- https://github.com/activepieces/activepieces/security/advisories/GHSA-5h2x-g6m3-grmq
- https://nvd.nist.gov/vuln/detail/CVE-2026-48499
- https://github.com/activepieces/activepieces/commit/9d8d328424bd32d295c5727af7550e1b57f9074d
