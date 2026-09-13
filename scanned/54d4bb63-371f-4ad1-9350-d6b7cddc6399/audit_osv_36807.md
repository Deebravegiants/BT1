# [M] Chartbrew: Insecure Direct Object Reference (IDOR) in Chart Operations

## Summary
Severity: Medium
Advisory: CVE-2026-25877
Aliases: GHSA-9fcr-x8x8-mrxc
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-03-06
Source: https://osv.dev/vulnerability/CVE-2026-25877
Type: osv

## Details
Chartbrew is an open-source web application that can connect directly to databases and APIs and use the data to create charts. Prior to version 4.8.1, the application performs authorization checks based solely on the project_id parameter when handling chart-related operations (update, delete, etc.). No authorization check is performed against the chart_id itself. This allows an authenticated user who has access to any project to manipulate or access charts belonging to other users/ project. This issue has been patched in version 4.8.1.

## References
- https://github.com/chartbrew/chartbrew/releases/tag/v4.8.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25877.json
- https://github.com/chartbrew/chartbrew/security/advisories/GHSA-9fcr-x8x8-mrxc
- https://nvd.nist.gov/vuln/detail/CVE-2026-25877
