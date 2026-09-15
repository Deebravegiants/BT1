# [H] Unexpected input to Update Channel Subscription endpoint causes DoS in Mattermost Confluence Plugin

## Summary
Severity: High
Advisory: CVE-2025-52931
Aliases: GHSA-vc77-c2hx-h5x2, GO-2025-3870
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-08-11
Source: https://osv.dev/vulnerability/CVE-2025-52931
Type: osv

## Details
Mattermost Confluence Plugin version <1.5.0 fails to handle unexpected request body which allows attackers to crash the plugin via constant hit to update channel subscription endpoint with an invalid request body.

## References
- https://github.com/mattermost/mattermost-plugin-confluence/
- https://mattermost.com/security-updates
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/52xxx/CVE-2025-52931.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-52931
