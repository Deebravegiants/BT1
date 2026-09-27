# [M] Mattermost Confluence Plugin has Improper Check for Unusual or Exceptional Conditions

## Summary
Severity: Medium
Advisory: GHSA-gjpm-6w34-ppvf
CVE: CVE-2025-54463
CWE: CWE-754
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-08-11
Source: https://github.com/advisories/GHSA-gjpm-6w34-ppvf
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-plugin-confluence` — affected >=0 <1.5.0

## Details
Mattermost Confluence Plugin versions < 1.5.0 fails to handle unexpected request bodies, allowing attackers to crash the plugin via constant hits to the server webhook endpoint with an invalid request body.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-54463
- https://github.com/mattermost/mattermost-plugin-confluence
- https://mattermost.com/security-updates
- https://pkg.go.dev/vuln/GO-2025-3866
