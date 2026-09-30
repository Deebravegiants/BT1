# [H] Chartbrew: Missing Authorization in /api/chart/:chart_id/query via team-level refresh toggle

## Summary
Severity: High
Advisory: CVE-2026-40601
Aliases: GHSA-cpr6-mhgm-893w
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-04-30
Source: https://osv.dev/vulnerability/CVE-2026-40601
Type: osv

## Details
Chartbrew is an open-source web application that can connect directly to databases and APIs and use the data to create charts. In version 4.9.0, Chartbrew exposes POST /api/chart/:chart_id/query without authentication. The endpoint only checks team.allowReportRefresh and does not verify that the target chart belongs to a public report, that the project is public, or that sharing policy allows the operation. An unauthenticated attacker who knows a chart identifier can trigger a data refresh and retrieve the current data of private charts. This issue has been patched in version 5.0.0.

## References
- https://github.com/chartbrew/chartbrew/releases/tag/v5.0.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40601.json
- https://github.com/chartbrew/chartbrew/security/advisories/GHSA-cpr6-mhgm-893w
- https://nvd.nist.gov/vuln/detail/CVE-2026-40601
