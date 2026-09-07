# [M] Mattermost does not validate requesting user permissions before updating admin details

## Summary
Severity: Medium
Advisory: GHSA-6xjj-v76v-fwpj
CVE: CVE-2023-4107
CWE: CWE-284, CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2023-08-11
Source: https://github.com/advisories/GHSA-6xjj-v76v-fwpj
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server/v6` — affected >=0 <7.8.8
- Go: `github.com/mattermost/mattermost-server/v6` — affected >=7.9.0 <7.9.6
- Go: `github.com/mattermost/mattermost-server/v6` — affected >=7.10.0 <7.10.4

## Details
Mattermost fails to properly validate the requesting user permissions when updating a system admin, allowing a user manager to update a system admin's details such as email, first name and last name.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-4107
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
