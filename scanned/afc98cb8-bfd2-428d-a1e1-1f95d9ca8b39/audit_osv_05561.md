# [H] BIT-gitlab-runner-2022-2251

## Summary
Severity: High
Advisory: BIT-gitlab-runner-2022-2251
Aliases: CVE-2022-2251
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-runner-2022-2251
Type: osv

## Affected
- Bitnami: `gitlab-runner` — affected >=15.5.0 <15.5.2

## Details
Improper sanitization of branch names in GitLab Runner affecting all versions prior to 15.3.5, 15.4 prior to 15.4.4, and 15.5 prior to 15.5.2 allows a user who creates a branch with a specially crafted name and gets another user to trigger a pipeline to execute commands in the runner as that other user.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-2251.json
- https://gitlab.com/gitlab-org/gitlab-runner/-/issues/27386
- https://hackerone.com/reports/1063511
- https://nvd.nist.gov/vuln/detail/CVE-2022-2251
