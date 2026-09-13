# [H] Mattermost Confluence Plugin is Missing Authentication for Critical Function

## Summary
Severity: High
Advisory: GHSA-6ff3-jgxh-vffj
CVE: CVE-2025-44004
CWE: CWE-306
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-08-11
Source: https://github.com/advisories/GHSA-6ff3-jgxh-vffj
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-plugin-confluence` — affected >=0 <1.5.0

## Details
Mattermost Confluence Plugin version <1.5.0 fails to check the authorization of the user to the Mattermost instance which allows attackers to create a channel subscription without proper authorization via API call to the create channel subscription endpoint.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-44004
- https://github.com/mattermost/mattermost-plugin-confluence
- https://mattermost.com/security-updates
