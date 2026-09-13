# [M] Full name disclosure via team top membership with Show Full Name option disabled

## Summary
Severity: Medium
Advisory: CVE-2023-5160
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2023-10-02
Source: https://osv.dev/vulnerability/CVE-2023-5160
Type: osv

## Details
Mattermost fails to check the Show Full Name option at the /api/v4/teams/TEAM_ID/top/team_members endpoint allowing a member to get the full name of another user even if the Show Full Name option was disabled

## References
- https://mattermost.com/security-updates
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/5xxx/CVE-2023-5160.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-5160
