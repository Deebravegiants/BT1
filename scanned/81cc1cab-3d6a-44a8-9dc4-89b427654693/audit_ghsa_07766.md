# [M] Mattermost Plugin Zoom fail to validate user identity and post ownership in the {{/api/v1/askPMI}} endpoint

## Summary
Severity: Medium
Advisory: GHSA-w65c-fvp5-fvc5
CVE: CVE-2026-0998
CWE: CWE-862
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-02-16
Source: https://github.com/advisories/GHSA-w65c-fvp5-fvc5
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-plugin-zoom` — affected >=0 <1.12.0

## Details
Mattermost versions 11.1.x <= 11.1.2, 10.11.x <= 10.11.9, 11.2.x <= 11.2.1 and Mattermost Plugin Zoom versions <=1.11.0 fail to validate user identity and post ownership in the {{/api/v1/askPMI}} endpoint which allows unauthorized users to start Zoom meetings as any user and overwrite arbitrary posts via direct API calls with manipulated user IDs and post data.. Mattermost Advisory ID: MMSA-2025-00534

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-0998
- https://github.com/mattermost/mattermost-plugin-zoom/commit/a8b58c43625ab25746e451acc4f71515d52c8122
- https://github.com/mattermost/mattermost-plugin-zoom
- https://mattermost.com/security-updates
