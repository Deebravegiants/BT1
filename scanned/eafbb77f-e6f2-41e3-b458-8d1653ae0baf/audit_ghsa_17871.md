# [M] Mattermost Confluence Plugin has Missing Authorization vulnerability

## Summary
Severity: Medium
Advisory: GHSA-qjrx-j8wm-xf83
CVE: CVE-2025-8285
CWE: CWE-862
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:N/I:L/A:N (CVSS_V3)
Published: 2025-08-11
Source: https://github.com/advisories/GHSA-qjrx-j8wm-xf83
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-plugin-confluence` — affected >=0 <1.5.0

## Details
Mattermost Confluence Plugin versions < 1.5.0 fail to check the access of the user to the channel which allows attackers to create channel subscription without proper access to the channel via API call to the create channel subscription endpoint.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-8285
- https://github.com/mattermost/mattermost-plugin-confluence
- https://mattermost.com/security-updates
- https://pkg.go.dev/vuln/GO-2025-3868
