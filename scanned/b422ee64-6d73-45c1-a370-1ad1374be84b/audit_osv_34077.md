# [H] Unauthenticated Channel Subscription Edit in Mattermost Confluence Plugin

## Summary
Severity: High
Advisory: CVE-2025-54478
Aliases: GHSA-qpjq-c5hr-7925, GO-2025-3875
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:N)
Published: 2025-08-11
Source: https://osv.dev/vulnerability/CVE-2025-54478
Type: osv

## Details
Mattermost Confluence Plugin version <1.5.0 fails to enforce authentication of the user to the Mattermost instance which allows unauthenticated attackers to edit channel subscriptions via API call to the edit channel subscription endpoint.

## References
- https://github.com/mattermost/mattermost-plugin-confluence/
- https://mattermost.com/security-updates
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/54xxx/CVE-2025-54478.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-54478
