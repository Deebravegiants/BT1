# [M] System Role with manage posts permission can read posts of Direct Messages

## Summary
Severity: Medium
Advisory: CVE-2023-5193
Aliases: GHSA-h8wh-f7gw-fwpr
CVSS: 4.9 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-09-29
Source: https://osv.dev/vulnerability/CVE-2023-5193
Type: osv

## Details
Mattermost fails to properly check permissions when retrieving a post allowing for a System Role with the permission to manage channels to read the posts of a DM conversation.

## References
- https://mattermost.com/security-updates
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/5xxx/CVE-2023-5193.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-5193
