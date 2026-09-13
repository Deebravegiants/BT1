# [M] Unauthorized Subscription Edit to Confluence Space in Mattermost Confluence Plugin

## Summary
Severity: Medium
Advisory: CVE-2025-48731
Aliases: GHSA-cmpr-8prq-w5p5, GO-2025-3861
CVSS: 6.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:N)
Published: 2025-08-11
Source: https://osv.dev/vulnerability/CVE-2025-48731
Type: osv

## Details
Mattermost Confluence Plugin version <1.5.0 fails to check the access of the user to the Confluence space which allows attackers to edit a subscription for a Confluence space the user does not have access for via edit subscription endpoint.

## References
- https://github.com/mattermost/mattermost-plugin-confluence/
- https://mattermost.com/security-updates
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/48xxx/CVE-2025-48731.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-48731
