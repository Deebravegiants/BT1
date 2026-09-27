# [M] OpenPanel report.list Queries Reports by an Unverified dashboardId, Crossing Organization Boundaries

## Summary
Severity: Medium
Advisory: CVE-2026-77769
Aliases: GHSA-3q95-vc6f-vc9v
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-21
Source: https://osv.dev/vulnerability/CVE-2026-77769
Type: osv

## Details
The report.list procedure in packages/trpc/src/routers/report.ts accepted a projectId and a dashboardId and returned getReportsByDashboardId(dashboardId). The enforceAccess middleware in packages/trpc/src/trpc.ts verified membership for the supplied projectId, but nothing verified that the supplied dashboardId belonged to that project, and getReportsByDashboardId in packages/db/src/services/reports.service.ts selects reports by dashboardId alone with no project scoping. An authenticated user could therefore pair a projectId from their own organization, which satisfies the middleware, with a dashboardId belonging to another organization and receive every report in that dashboard. A correctly scoped helper, listReportsCore, already existed in the same service file and resolves the dashboard through getDashboardById(dashboardId, projectId) before returning reports, but the router did not use it.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/77xxx/CVE-2026-77769.json
- https://github.com/Openpanel-dev/openpanel/security/advisories/GHSA-3q95-vc6f-vc9v
- https://nvd.nist.gov/vuln/detail/CVE-2026-77769
- https://www.vulncheck.com/advisories/openpanel-report-list-queries-reports-by-an-unverified-dashboardid-crossing-organization-boundaries
- https://github.com/Openpanel-dev/openpanel/commit/0a51b6805eed0b3da8376175acd5fa3d26819cb6
- https://github.com/Openpanel-dev/openpanel
- https://github.com/Openpanel-dev/openpanel/blob/e8a0602cda5a4d4b463f11d298a1b078c446bf33/packages/trpc/src/routers/report.ts
