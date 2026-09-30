# [M] BIT-gitlab-2021-22187

## Summary
Severity: Medium
Advisory: BIT-gitlab-2021-22187
Aliases: CVE-2021-22187
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2021-22187
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=13.8.0 <13.8.4

## Details
An issue has been discovered in GitLab affecting all versions of Gitlab EE/CE before 13.6.7. A potential resource exhaustion issue that allowed running or pending jobs to continue even after project was deleted.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2021/CVE-2021-22187.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/300452
- https://nvd.nist.gov/vuln/detail/CVE-2021-22187
