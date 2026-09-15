# [H] Improper Isolation or Compartmentalization in GitLab

## Summary
Severity: High
Advisory: BIT-gitlab-2024-6323
Aliases: CVE-2024-6323
Ecosystem: Bitnami
Published: 2024-06-28
Source: https://osv.dev/vulnerability/BIT-gitlab-2024-6323
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=17.1.0 <17.1.1

## Details
Improper authorization in global search in GitLab EE affecting all versions from 16.11 prior to 16.11.5 and 17.0 prior to 17.0.3 and 17.1 prior to 17.1.1 allows an attacker leak content of a private repository in a public project.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/457912
- https://nvd.nist.gov/vuln/detail/CVE-2024-6323
