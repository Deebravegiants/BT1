# [M] Exposure of Sensitive System Information to an Unauthorized Control Sphere in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2024-10240
Aliases: CVE-2024-10240
Ecosystem: Bitnami
Published: 2024-11-28
Source: https://osv.dev/vulnerability/BIT-gitlab-2024-10240
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=17.5.0 <17.5.2

## Details
An issue has been discovered in GitLab EE affecting all versions starting from 17.3 before 17.3.7, all versions starting from 17.4 before 17.4.4, all versions starting from 17.5 before 17.5.2 in which an unauthenticated user may be able to read some information about an MR in a private project, under certain circumstances.

## References
- https://about.gitlab.com/releases/2024/11/13/patch-release-gitlab-17-5-2-released/#information-disclosure-through-an-api-endpoint
- https://gitlab.com/gitlab-org/gitlab/-/issues/493188
- https://nvd.nist.gov/vuln/detail/CVE-2024-10240
