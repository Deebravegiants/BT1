# [H] Mattermost Confluence plugin doesn't properly escape user-controlled display names in HTML template rendering

## Summary
Severity: High
Advisory: GHSA-ffx7-34p2-vm3w
CVE: CVE-2025-13523
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-02-06
Source: https://github.com/advisories/GHSA-ffx7-34p2-vm3w
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-plugin-confluence` — affected >=0 <1.7.0

## Details
Mattermost Confluence plugin version < 1.7.0 fails to properly escape user-controlled display names in HTML template rendering which allows authenticated Confluence users with malicious display names to execute arbitrary JavaScript in victim browsers via sending a specially crafted OAuth2 connection link that, when visited, renders the attacker's display name without proper sanitization. Mattermost Advisory ID: MMSA-2025-00557

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-13523
- https://github.com/mattermost/mattermost-plugin-confluence
- https://mattermost.com/security-updates
