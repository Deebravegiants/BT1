# [M] Playbook run link to private channel grants channel access

## Summary
Severity: Medium
Advisory: CVE-2024-32045
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:L/A:N)
Published: 2024-05-26
Source: https://osv.dev/vulnerability/CVE-2024-32045
Type: osv

## Details
Mattermost versions 9.5.x <= 9.5.3, 9.6.x <= 9.6.1, 8.1.x <= 8.1.12 fail to enforce proper access controls for channel and team membership when linking a playbook run to a channel which allows  members to link their runs to private channels they were not members of.

## References
- https://mattermost.com/security-updates
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/32xxx/CVE-2024-32045.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-32045
