# [H] Incorrect Authorization in GitLab

## Summary
Severity: High
Advisory: BIT-gitlab-2023-5356
Aliases: CVE-2023-5356
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2023-5356
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=16.7.0 <16.7.2

## Details
Incorrect authorization checks in GitLab CE/EE from all versions starting from 8.13 before 16.5.6, all versions starting from 16.6 before 16.6.4, all versions starting from 16.7 before 16.7.2, allows a user to abuse slack/mattermost integrations to execute slash commands as another user.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/427154
- https://hackerone.com/reports/2188868
- https://nvd.nist.gov/vuln/detail/CVE-2023-5356
