# [M] Channel metadata visible in archived channels despite configuration setting

## Summary
Severity: Medium
Advisory: CVE-2025-27571
Aliases: GHSA-h4rr-f37j-4hh7, GO-2025-3619
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2025-04-16
Source: https://osv.dev/vulnerability/CVE-2025-27571
Type: osv

## Details
Mattermost versions 10.5.x <= 10.5.1, 10.4.x <= 10.4.3, 9.11.x <= 9.11.9 fail to check the "Allow Users to View Archived Channels" configuration when fetching channel metadata of a post from archived channels, which allows authenticated users to access such information when a channel is archived.

## References
- https://mattermost.com/security-updates
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/27xxx/CVE-2025-27571.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-27571
