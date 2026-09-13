# [M] Chartbrew: Unauthenticated Chart Filter Endpoint: POST /project/:project_id/chart/:chart_id/filter missing verifyToken + checkPermissions

## Summary
Severity: Medium
Advisory: CVE-2026-27603
Aliases: GHSA-9fhr-5vvc-p455
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-03-06
Source: https://osv.dev/vulnerability/CVE-2026-27603
Type: osv

## Details
Chartbrew is an open-source web application that can connect directly to databases and APIs and use the data to create charts. Prior to version 4.8.4, the chart filter endpoint POST /project/:project_id/chart/:chart_id/filter is missing both verifyToken and checkPermissions middleware, allowing unauthenticated users to access chart data from any team/project. This issue has been patched in version 4.8.4.

## References
- https://github.com/chartbrew/chartbrew/releases/tag/v4.8.4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27603.json
- https://github.com/chartbrew/chartbrew/security/advisories/GHSA-9fhr-5vvc-p455
- https://nvd.nist.gov/vuln/detail/CVE-2026-27603
