# [M] BIT-mattermost-2023-46701

## Summary
Severity: Medium
Advisory: BIT-mattermost-2023-46701
Aliases: CVE-2023-46701
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mattermost-2023-46701
Type: osv

## Affected
- Bitnami: `mattermost` — affected >=9.2.0 <9.2.2

## Details
Mattermost fails to perform authorization checks in the  /plugins/playbooks/api/v0/runs/add-to-timeline-dialog endpoint of the Playbooks plugin allowing an attacker to get limited information about a post if they know the post ID

## References
- https://mattermost.com/security-updates
- https://nvd.nist.gov/vuln/detail/CVE-2023-46701
