# [M] Slash commands run in channel without channel membership via playbook task commands

## Summary
Severity: Medium
Advisory: CVE-2024-29215
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)
Published: 2024-05-26
Source: https://osv.dev/vulnerability/CVE-2024-29215
Type: osv

## Details
Mattermost versions 9.5.x <= 9.5.3, 9.7.x <= 9.7.1, 9.6.x <= 9.6.1, 8.1.x <= 8.1.12 fail to enforce proper access control which allows a user to run a slash command in a channel they are not a member of via linking a playbook run to that channel and running a slash command as a playbook task command.

## References
- https://mattermost.com/security-updates
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/29xxx/CVE-2024-29215.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-29215
