# [M] Unauthorized View Access to Archived Channel Member Info

## Summary
Severity: Medium
Advisory: CVE-2025-2564
Aliases: GHSA-mj2p-v2c2-vh4v, GO-2025-3623
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2025-04-16
Source: https://osv.dev/vulnerability/CVE-2025-2564
Type: osv

## Details
Mattermost versions 10.5.x <= 10.5.1, 10.4.x <= 10.4.3, 9.11.x <= 9.11.9 fail to properly enforce the 'Allow users to view/update archived channels' System Console setting, which allows authenticated users to view members and member information of archived channels even when this setting is disabled.

## References
- https://mattermost.com/security-updates
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/2xxx/CVE-2025-2564.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-2564
