# [M] BIT-gitlab-2021-22211

## Summary
Severity: Medium
Advisory: BIT-gitlab-2021-22211
Aliases: CVE-2021-22211
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2021-22211
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=13.11.0 <13.11.2

## Details
An issue has been discovered in GitLab CE/EE affecting all versions starting from 13.7. GitLab Dependency Proxy, under certain circumstances, can impersonate a user resulting in possibly incorrect access handling.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2021/CVE-2021-22211.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/298847
- https://nvd.nist.gov/vuln/detail/CVE-2021-22211
