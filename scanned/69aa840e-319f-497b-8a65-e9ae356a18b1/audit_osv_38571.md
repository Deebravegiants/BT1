# [H] Chartbrew: Incorrect Access Control in public chart and export routes via missing onReport and SharePolicy checks

## Summary
Severity: High
Advisory: CVE-2026-40595
Aliases: GHSA-mq7q-6xh6-5649
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-04-30
Source: https://osv.dev/vulnerability/CVE-2026-40595
Type: osv

## Details
Chartbrew is an open-source web application that can connect directly to databases and APIs and use the data to create charts. In version 4.9.0, Chartbrew exposes public chart retrieval and export routes that only verify project-level public access and, for exports, a team-level export toggle. The routes do not verify whether the target chart is actually allowed on the public report or whether the governing SharePolicy permits public access. An unauthenticated attacker who knows a chart identifier in a public project can read or export chart data for charts that were intentionally hidden from the report. This issue has been patched in version 5.0.0.

## References
- https://github.com/chartbrew/chartbrew/releases/tag/v5.0.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40595.json
- https://github.com/chartbrew/chartbrew/security/advisories/GHSA-mq7q-6xh6-5649
- https://nvd.nist.gov/vuln/detail/CVE-2026-40595
