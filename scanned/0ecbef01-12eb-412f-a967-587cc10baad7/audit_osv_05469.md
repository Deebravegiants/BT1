# [M] Incorrect Authorization in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2024-9623
Aliases: CVE-2024-9623
Ecosystem: Bitnami
Published: 2024-10-13
Source: https://osv.dev/vulnerability/BIT-gitlab-2024-9623
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=17.4.0 <17.4.2

## Details
An issue was discovered in GitLab CE/EE affecting all versions starting from 8.16 prior to 17.2.9, starting from 17.3 prior to 17.3.5, and starting from 17.4 prior to 17.4.2, which allows deploy keys to push to an archived repository.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/459995
- https://nvd.nist.gov/vuln/detail/CVE-2024-9623
