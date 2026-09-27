# [M] Snipe-IT 8.6.4 before 8.7.0 Permission Bypass via assigned components

## Summary
Severity: Medium
Advisory: CVE-2026-86764
Aliases: GHSA-v973-fm42-f8xv
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-09
Source: https://osv.dev/vulnerability/CVE-2026-86764
Type: osv

## Details
Snipe-IT through 8.6.4 (fixed in 8.7.0) does not enforce the components.view permission on the authenticated endpoint GET /api/v1/hardware/<asset-id>/assigned/components. The endpoint authorizes only assets.view on the parent asset before returning linked component details; the components.view check is applied only to the response's available_actions.view flag and not to the returned data. As a result, an authenticated user holding only assets.view can enumerate component IDs, names, assigned quantities, and notes that are otherwise protected — the direct GET /api/v1/components/<id> endpoint correctly returns 403 Forbidden for such users.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/86xxx/CVE-2026-86764.json
- https://github.com/grokability/snipe-it/security/advisories/GHSA-v973-fm42-f8xv
- https://nvd.nist.gov/vuln/detail/CVE-2026-86764
- https://www.vulncheck.com/advisories/snipe-it-8.6.4-before-8.7.0-permission-bypass-via-assigned-components
