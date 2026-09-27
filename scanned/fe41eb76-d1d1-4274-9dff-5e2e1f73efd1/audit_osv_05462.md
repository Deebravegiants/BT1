# [M] Incorrect Authorization in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2024-8650
Aliases: CVE-2024-8650
Ecosystem: Bitnami
Published: 2024-12-18
Source: https://osv.dev/vulnerability/BIT-gitlab-2024-8650
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=17.6.0 <17.6.2

## Details
An issue was discovered in GitLab CE/EE affecting all versions from 15.0 prior to 17.4.6, 17.5 prior to 17.5.4, and 17.6 prior to 17.6.2 that allowed non-member users to view unresolved threads marked as internal notes in public projects merge requests.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/486300
- https://hackerone.com/reports/2705909
- https://nvd.nist.gov/vuln/detail/CVE-2024-8650
