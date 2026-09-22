# [M] Reconmap Report Preview Endpoint Is Marked AllowAnonymous, Exposing Every Project and Client Organisation Without Authentication

## Summary
Severity: Medium
Advisory: CVE-2026-77767
Aliases: GHSA-mhrh-jfmr-8mmw
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-21
Source: https://osv.dev/vulnerability/CVE-2026-77767
Type: osv

## Details
Reconmap's API applies a fallback authorization policy in apps/api/app/Program.cs that requires an authenticated user holding the administrator role, so controllers without their own attribute reject anonymous callers. The report preview action in apps/api/app/Controllers/ReportsController.cs carries [AllowAnonymous] and therefore opts out of that policy. PreviewReport loads the Project row named by the id path segment, loads the linked Organisation through the project's ClientId, and renders both into default-report-template.html, which prints the project name and description together with the client organisation's name, address and URL. No authentication, project membership or role check is performed. Because the id is the auto-increment primary key of the project table, an unauthenticated remote caller can walk sequential ids to retrieve the engagement details and client organisation of every project on the instance, and the 404 returned for a missing id reveals which project ids exist. Reconmap stores penetration-testing engagements, so the disclosed descriptions and client records are sensitive by nature.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/77xxx/CVE-2026-77767.json
- https://github.com/reconmap/reconmap/security/advisories/GHSA-mhrh-jfmr-8mmw
- https://nvd.nist.gov/vuln/detail/CVE-2026-77767
- https://www.vulncheck.com/advisories/reconmap-report-preview-endpoint-is-marked-allowanonymous-exposing-every-project-and-client-organisation-without-authentication
- https://github.com/reconmap/reconmap/commit/2b2eb0cf0aa95726b4edd0045f86d2dcdb8de34d
- https://github.com/reconmap/reconmap
- https://github.com/reconmap/reconmap/blob/56ca3748343a50c98185d53827172d8f13a6ad0f/apps/api/app/Controllers/ReportsController.cs
- https://github.com/reconmap/reconmap/blob/56ca3748343a50c98185d53827172d8f13a6ad0f/apps/api/app/Program.cs
