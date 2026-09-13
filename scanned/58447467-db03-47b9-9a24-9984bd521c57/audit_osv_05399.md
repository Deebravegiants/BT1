# [H] Incorrect Authorization in GitLab

## Summary
Severity: High
Advisory: BIT-gitlab-2023-4379
Aliases: CVE-2023-4379
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2023-4379
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=16.4.0 <16.4.1

## Details
An issue has been discovered in GitLab EE affecting all versions starting from 15.3 prior to 16.2.8, 16.3 prior to 16.3.5, and 16.4 prior to 16.4.1. Code owner approval was not removed from merge requests when the target branch was updated.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/415496
- https://nvd.nist.gov/vuln/detail/CVE-2023-4379
