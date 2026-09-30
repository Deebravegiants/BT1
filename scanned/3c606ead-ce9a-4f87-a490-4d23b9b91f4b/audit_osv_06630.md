# [M] BIT-mattermost-2023-6547

## Summary
Severity: Medium
Advisory: BIT-mattermost-2023-6547
Aliases: CVE-2023-6547
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mattermost-2023-6547
Type: osv

## Affected
- Bitnami: `mattermost` — affected >=9.2.0 <9.2.2

## Details
Mattermost fails to validate team membership when a user attempts to access a playbook, allowing a user with permissions to a playbook but no permissions to the team the playbook is on to access and modify the playbook. This can happen if the user was once a member of the team, got permissions to the playbook and was then removed from the team.

## References
- https://mattermost.com/security-updates
- https://nvd.nist.gov/vuln/detail/CVE-2023-6547
