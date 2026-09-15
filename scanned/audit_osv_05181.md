# [H] BIT-gitlab-2022-0738

## Summary
Severity: High
Advisory: BIT-gitlab-2022-0738
Aliases: CVE-2022-0738
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-0738
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.8.0 <14.8.2

## Details
An issue has been discovered in GitLab affecting all versions starting from 14.6 before 14.6.5, all versions starting from 14.7 before 14.7.4, all versions starting from 14.8 before 14.8.2. GitLab was leaking user passwords when adding mirrors with SSH credentials under specific conditions.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-0738.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/27395
- https://nvd.nist.gov/vuln/detail/CVE-2022-0738
