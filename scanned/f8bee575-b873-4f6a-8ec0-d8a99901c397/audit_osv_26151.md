# [M] A team member can soft delete other teams that they are not part of

## Summary
Severity: Medium
Advisory: CVE-2023-5195
Aliases: GHSA-9hwp-cj7m-wjw4
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-09-29
Source: https://osv.dev/vulnerability/CVE-2023-5195
Type: osv

## Details
Mattermost fails to properly validate the permissions when soft deleting a team allowing a team member to soft delete other teams that they are not part of

## References
- https://mattermost.com/security-updates
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/5xxx/CVE-2023-5195.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-5195
