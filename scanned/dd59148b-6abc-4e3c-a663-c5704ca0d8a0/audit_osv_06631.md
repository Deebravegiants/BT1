# [M] BIT-mattermost-2023-6727

## Summary
Severity: Medium
Advisory: BIT-mattermost-2023-6727
Aliases: CVE-2023-6727
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mattermost-2023-6727
Type: osv

## Affected
- Bitnami: `mattermost` — affected >=9.2.0 <9.2.2

## Details
Mattermost fails to perform correct authorization checks when creating a playbook action, allowing users without access to the playbook to create playbook actions. If the playbook action created is to post a message in a channel based on specific keywords in a post, some playbook information, like the name, can be leaked.

## References
- https://mattermost.com/security-updates
- https://nvd.nist.gov/vuln/detail/CVE-2023-6727
