# [C] SuperPlane < 0.27.0 Broken Object Level Authorization via CanvasService gRPC

## Summary
Severity: Critical
Advisory: CVE-2026-57510
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-28
Source: https://osv.dev/vulnerability/CVE-2026-57510
Type: osv

## Details
SuperPlane before 0.27.0 contains a broken object-level authorization vulnerability in the CanvasService gRPC handlers that allows authenticated users with viewer-level access to one organization to access resources belonging to other organizations by supplying arbitrary canvas or queue UUIDs without organization scoping. Attackers can read cross-tenant execution history and event payloads containing sensitive secrets, write queue items and canvas events into victim organizations, delete arbitrary canvases, and disrupt automation workflows across tenant boundaries.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/57xxx/CVE-2026-57510.json
- https://github.com/superplanehq/superplane/releases/tag/v0.27.0
- https://nvd.nist.gov/vuln/detail/CVE-2026-57510
- https://www.vulncheck.com/advisories/superplane-broken-object-level-authorization-via-canvasservice-grpc
- https://github.com/superplanehq/superplane/pull/5635
- https://github.com/superplanehq/superplane/commit/3e45cf4f1b5f1be9fbbfd90c97960a73f00f897b
- https://github.com/superplanehq/superplane
