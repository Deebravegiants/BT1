# [M] BIT-mattermost-2023-49874

## Summary
Severity: Medium
Advisory: BIT-mattermost-2023-49874
Aliases: CVE-2023-49874
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mattermost-2023-49874
Type: osv

## Affected
- Bitnami: `mattermost` — affected >=9.2.0 <9.2.2

## Details
Mattermost fails to check whether a user is a guest when updating the tasks of a private playbook run allowing a guest to update the tasks of a private playbook run if they know the run ID.

## References
- https://mattermost.com/security-updates
- https://nvd.nist.gov/vuln/detail/CVE-2023-49874
