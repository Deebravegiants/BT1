# [M] OpenPanel report.get Returns Any Report by Identifier Without Checking Project Access

## Summary
Severity: Medium
Advisory: CVE-2026-77768
Aliases: GHSA-9x7c-f87x-2243
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-21
Source: https://osv.dev/vulnerability/CVE-2026-77768
Type: osv

## Details
The report.get procedure in packages/trpc/src/routers/report.ts accepted only a reportId and returned getReportById(reportId) directly. The enforceAccess middleware in packages/trpc/src/trpc.ts evaluates membership only when the input carries a projectId or organizationId key, so an input consisting of a reportId alone passed through unchecked, and getReportById in packages/db/src/services/reports.service.ts performs a findUnique on the report id with no project scoping. Any authenticated user could therefore read the full configuration of any saved report on the instance, including the owning projectId, event series, filters, breakdowns and formulas, by supplying its identifier. The adjacent update, delete and duplicate procedures resolve the report first and check getProjectAccess against the report's own projectId, so the omission was specific to this procedure.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/77xxx/CVE-2026-77768.json
- https://github.com/Openpanel-dev/openpanel/security/advisories/GHSA-9x7c-f87x-2243
- https://nvd.nist.gov/vuln/detail/CVE-2026-77768
- https://www.vulncheck.com/advisories/openpanel-report-get-returns-any-report-by-identifier-without-checking-project-access
- https://github.com/Openpanel-dev/openpanel/commit/0a51b6805eed0b3da8376175acd5fa3d26819cb6
- https://github.com/Openpanel-dev/openpanel
- https://github.com/Openpanel-dev/openpanel/blob/e8a0602cda5a4d4b463f11d298a1b078c446bf33/packages/trpc/src/routers/report.ts
