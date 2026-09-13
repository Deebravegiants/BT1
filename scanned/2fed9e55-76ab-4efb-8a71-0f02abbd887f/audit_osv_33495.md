# [M] Unauthorized Channel Subscription Read in Mattermost Confluence Plugin

## Summary
Severity: Medium
Advisory: CVE-2025-44001
Aliases: GHSA-vpcr-fqpc-386h, GO-2025-3863
CVSS: 4.0 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:L/I:N/A:N)
Published: 2025-08-11
Source: https://osv.dev/vulnerability/CVE-2025-44001
Type: osv

## Details
Mattermost Confluence Plugin version <1.5.0 fails to check the access of the user to the channel which allows attackers to get channel subscription details without proper access to the channel via API call to the Get Channel Subscriptions details endpoint.

## References
- https://github.com/mattermost/mattermost-plugin-confluence/
- https://mattermost.com/security-updates
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/44xxx/CVE-2025-44001.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-44001
