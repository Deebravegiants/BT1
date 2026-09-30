# [M] Unexpected Input to Server Webhook endpoint Causes DoS in Mattermost Confluence Plugin

## Summary
Severity: Medium
Advisory: CVE-2025-53514
Aliases: GHSA-w92j-c6gr-hj8r, GO-2025-3871
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-08-11
Source: https://osv.dev/vulnerability/CVE-2025-53514
Type: osv

## Details
Mattermost Confluence Plugin version <1.5.0 fails to handle unexpected request body which allows attackers to crash the plugin via constant hit to server webhook endpoint with an invalid request body.

## References
- https://github.com/mattermost/mattermost-plugin-confluence/
- https://mattermost.com/security-updates
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/53xxx/CVE-2025-53514.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-53514
