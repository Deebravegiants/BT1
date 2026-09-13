# [H] Incorrect Authorization in GitLab

## Summary
Severity: High
Advisory: BIT-gitlab-2023-5106
Aliases: CVE-2023-5106
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2023-5106
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=16.4.0 <16.4.1

## Details
An issue has been discovered in Ultimate-licensed GitLab EE affecting all versions starting 13.12 prior to 16.2.8, 16.3.0 prior to 16.3.5, and 16.4.0 prior to 16.4.1 that could allow an attacker to impersonate users in CI pipelines through direct transfer group imports.

## References
- https://gitlab.com/gitlab-org/gitlab/-/commit/67039cfcae80b8fc0496f79be88714873cd169b3
- https://gitlab.com/gitlab-org/security/gitlab/-/issues/980
- https://nvd.nist.gov/vuln/detail/CVE-2023-5106
