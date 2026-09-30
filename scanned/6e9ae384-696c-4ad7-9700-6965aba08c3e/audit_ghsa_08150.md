# [M] Mattermost Plugin Zoom allows any logged-in user to change Zoom meeting restrictions for arbitrary channels

## Summary
Severity: Medium
Advisory: GHSA-2phx-frhf-xr55
CVE: CVE-2026-0997
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-02-16
Source: https://github.com/advisories/GHSA-2phx-frhf-xr55
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-plugin-zoom` — affected >=0 <1.11.0

## Details
Mattermost versions 11.1.x <= 11.1.2, 10.11.x <= 10.11.9, 11.2.x <= 11.2.1 and Mattermost Plugin Zoom versions <=1.11.0 fail to validate the authenticated user when processing {{/plugins/zoom/api/v1/channel-preference}}, which allows any logged-in user to change Zoom meeting restrictions for arbitrary channels via crafted API requests.. Mattermost Advisory ID: MMSA-2025-00558

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-0997
- https://github.com/mattermost/mattermost-plugin-zoom/commit/a8b58c43625ab25746e451acc4f71515d52c8122
- https://github.com/mattermost/mattermost-plugin-zoom
- https://mattermost.com/security-updates
