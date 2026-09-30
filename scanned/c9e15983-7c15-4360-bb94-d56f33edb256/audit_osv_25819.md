# [M] Users full name disclosure through Mattermost Boards with Show Full Name Option disabled

## Summary
Severity: Medium
Advisory: CVE-2023-45223
Aliases: GHSA-p5pr-vm3j-jxxf
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2023-11-27
Source: https://osv.dev/vulnerability/CVE-2023-45223
Type: osv

## Details
Mattermost fails to properly validate the "Show Full Name" option in a few endpoints in Mattermost Boards, allowing a member to get the full name of another user even if the Show Full Name option was disabled.

## References
- https://mattermost.com/security-updates
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/45xxx/CVE-2023-45223.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-45223
