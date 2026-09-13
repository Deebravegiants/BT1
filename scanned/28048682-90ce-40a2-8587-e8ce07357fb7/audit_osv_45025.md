# [M] Remote cluster metadata enumeration via /share-channel autocomplete

## Summary
Severity: Medium
Advisory: CVE-2026-9824
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-07-13
Source: https://osv.dev/vulnerability/CVE-2026-9824
Type: osv

## Details
Mattermost versions 11.7.x <= 11.7.2, 11.6.x <= 11.6.4, 10.11.x <= 10.11.19 fail to check the manage_shared_channels permission in the /share-channel autocomplete handler, which allows an authenticated user without that permission to enumerate configured remote cluster connection metadata via slash command autocomplete.. Mattermost Advisory ID: MMSA-2026-00676

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/9xxx/CVE-2026-9824.json
- https://mattermost.com/security-updates
- https://nvd.nist.gov/vuln/detail/CVE-2026-9824
