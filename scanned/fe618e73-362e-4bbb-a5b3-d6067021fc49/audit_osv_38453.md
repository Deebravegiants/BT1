# [M] Plane: ORM Field Reference Injection via `segment` Parameter in Saved Analytics

## Summary
Severity: Medium
Advisory: CVE-2026-40102
Aliases: GHSA-93x3-ghh7-72j3
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-05-20
Source: https://osv.dev/vulnerability/CVE-2026-40102
Type: osv

## Details
Plane is an open-source project management tool. In versions 1.3.0 and below, SavedAnalyticEndpoint passes the user-controlled segment query parameter directly to a Django F() expression without validation (unlike the regular AnalyticsEndpoint, which checks against an allowlist), causing ORM Field Reference Injection. An authenticated workspace MEMBER can send GET /api/workspaces/<slug>/saved-analytic-view/<analytic_id>/ with a crafted segment value that is forwarded into build_graph_plot() and traverses foreign-key relationships (e.g. workspace__owner__password) before being projected via .values("dimension", "segment"), returning the referenced field values directly in the JSON response. This exposes sensitive data such as bcrypt password hashes, API tokens, and related users' email addresses, making it a stronger primitive than the related order_by injection where values are only leaked through ordering. This issue has been fixed in version 1.3.1.

## References
- https://github.com/makeplane/plane/releases/tag/v1.3.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40102.json
- https://github.com/makeplane/plane/security/advisories/GHSA-93x3-ghh7-72j3
- https://nvd.nist.gov/vuln/detail/CVE-2026-40102
