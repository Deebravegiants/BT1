# [M] Improper Control of a Resource Through its Lifetime in Mattermost

## Summary
Severity: Medium
Advisory: GHSA-fxwj-v664-wv5g
CVE: CVE-2022-1385
CWE: CWE-664, CWE-668
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-04-20
Source: https://github.com/advisories/GHSA-fxwj-v664-wv5g
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server/v6` — affected >=0 <6.5.0

## Details
Mattermost 6.4.x and earlier fails to properly invalidate pending email invitations when the action is performed from the system console, which allows accidentally invited users to join the workspace and access information from the public teams and channels.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-1385
- https://hackerone.com/reports/1486820
- https://github.com/mattermost/mattermost-server
- https://mattermost.com/security-updates
